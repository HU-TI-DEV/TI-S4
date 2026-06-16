#include <gz/transport.hh>
#include <gz/msgs/pointcloud_packed.pb.h>

#include <pcl/point_types.h>
#include <pcl/point_cloud.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/segmentation/sac_segmentation.h>
#include <pcl/filters/extract_indices.h>
#include <pcl/search/kdtree.h>
#include <pcl/segmentation/extract_clusters.h>

#include <iostream>
#include <memory>
#include <vector>
#include <cmath>
#include <cstring>
#include <thread>

class LidarProcessor
{
public:

    float voxelSize = 0.06f;

    float clusterTolerance = 0.30f;
    int minClusterSize = 60;
    int maxClusterSize = 20000;

    float maxRange = 30.0f;

    // callback for incoming point cloud messages
    void OnPointCloud(const gz::msgs::PointCloudPacked &msg)
    {
        auto cloud = std::make_shared<pcl::PointCloud<pcl::PointXYZ>>();

        const std::string &data = msg.data();
        const int step = msg.point_step();
        const int total = msg.width() * msg.height();

        if (total <= 0 || data.empty())
            return;

        //decode the point cloud data into a PCL point cloud
        for (int i = 0; i < total; i++)
        {
            const char *ptr = data.data() + i * step;

            float x, y, z;
            std::memcpy(&x, ptr + 0, 4);
            std::memcpy(&y, ptr + 4, 4);
            std::memcpy(&z, ptr + 8, 4);

            if (!std::isfinite(x) || !std::isfinite(y) || !std::isfinite(z))
                continue;

            float r = std::sqrt(x*x + y*y + z*z);
            if (r > maxRange)
                continue;

            cloud->push_back(pcl::PointXYZ(x, y, z));
        }

        if (cloud->empty())
            return;

        // voxel downsample the point cloud to reduce noise and speed up processing
        auto voxel = std::make_shared<pcl::PointCloud<pcl::PointXYZ>>();
        pcl::VoxelGrid<pcl::PointXYZ> vg;
        vg.setInputCloud(cloud);
        vg.setLeafSize(voxelSize, voxelSize, voxelSize);
        vg.filter(*voxel);

        if (voxel->empty())
            return;

        // ransac ground removal
        auto noGround = RemoveGround(voxel);

        if (noGround->size() < minClusterSize)
            return;

        // cluster the point cloud into separate objects
        auto clusters = Cluster(noGround);

        std::cout << "\n========== CALLBACK ==========\n";
        std::cout << "[INFO] raw points: " << total << "\n";
        std::cout << "[INFO] voxel: " << voxel->size() << "\n";
        std::cout << "[INFO] non-ground: " << noGround->size() << "\n";
        std::cout << "[INFO] clusters: " << clusters.size() << "\n";

        int id = 0;
        for (auto &c : clusters)
        {
            if (c->size() < minClusterSize)
                continue;

            if (RejectBumps(c))
                continue;

            Print(c, id++);
        }
    }

    // ground removal using RANSAC plane fitting
    pcl::PointCloud<pcl::PointXYZ>::Ptr
    RemoveGround(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud)
    {
        pcl::SACSegmentation<pcl::PointXYZ> seg;
        pcl::PointIndices::Ptr inliers(new pcl::PointIndices);
        pcl::ModelCoefficients::Ptr coeff(new pcl::ModelCoefficients);

        seg.setOptimizeCoefficients(true);
        seg.setModelType(pcl::SACMODEL_PLANE);
        seg.setMethodType(pcl::SAC_RANSAC);

        seg.setDistanceThreshold(0.07);  
        seg.setMaxIterations(100);
        seg.setInputCloud(cloud);
        seg.segment(*inliers, *coeff);

        pcl::ExtractIndices<pcl::PointXYZ> extract;
        extract.setInputCloud(cloud);
        extract.setIndices(inliers);
        extract.setNegative(true);

        auto out = std::make_shared<pcl::PointCloud<pcl::PointXYZ>>();
        extract.filter(*out);

        return out;
    }

    // cluster the point cloud into separate objects
    std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr>
    Cluster(pcl::PointCloud<pcl::PointXYZ>::Ptr cloud)
    {
        std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr> clusters;

        pcl::search::KdTree<pcl::PointXYZ>::Ptr tree(new pcl::search::KdTree<pcl::PointXYZ>);
        tree->setInputCloud(cloud);

        std::vector<pcl::PointIndices> indices;

        pcl::EuclideanClusterExtraction<pcl::PointXYZ> ec;
        ec.setClusterTolerance(clusterTolerance);
        ec.setMinClusterSize(minClusterSize);
        ec.setMaxClusterSize(maxClusterSize);
        ec.setSearchMethod(tree);
        ec.setInputCloud(cloud);
        ec.extract(indices);

        for (auto &i : indices)
        {
            auto c = std::make_shared<pcl::PointCloud<pcl::PointXYZ>>();

            for (auto idx : i.indices)
                c->push_back(cloud->points[idx]);

            clusters.push_back(c);
        }

        return clusters;
    }

    // filter out small bumps that are likely noise
    bool RejectBumps(pcl::PointCloud<pcl::PointXYZ>::Ptr c)
    {
        double minZ = 1e9, maxZ = -1e9;

        for (auto &p : c->points)
        {
            minZ = std::min(minZ, (double)p.z);
            maxZ = std::max(maxZ, (double)p.z);
        }

        double height = maxZ - minZ;

        // remove bumps that are too small
        if (height < 0.10)
            return true;

        return false;
    }

    // print cluster info
    void Print(pcl::PointCloud<pcl::PointXYZ>::Ptr c, int id)
    {
        double cx = 0, cy = 0, cz = 0;

        for (auto &p : c->points)
        {
            cx += p.x;
            cy += p.y;
            cz += p.z;
        }

        cx /= c->size();
        cy /= c->size();
        cz /= c->size();

        double dist = std::sqrt(cx*cx + cy*cy + cz*cz);

        std::cout << "\n BLOCK " << id << "\n";
        std::cout << "points: " << c->size() << "\n";
        std::cout << "center: (" << cx << "," << cy << "," << cz << ")\n";
        std::cout << "distance: " << dist << "\n";
    }
};

int main()
{
    gz::transport::Node node;
    LidarProcessor proc;

    std::cout << "Waiting for lidar...\n";

    node.Subscribe("/digger/lidar/points/points",
                   &LidarProcessor::OnPointCloud,
                   &proc);

    while (true)
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
}