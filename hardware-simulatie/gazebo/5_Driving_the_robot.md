Dit stsuk nog verwerken:


TODOOOOOO




  // Create a transport node and advertise a topic.
  gz::transport::Node node;
  std::string topic = "/cmd_vel";

  auto pub = node.Advertise<gz::msgs::Twist>(topic);
  if (!pub)
  {
    std::cerr << "Error advertising topic [" << topic << "]" << std::endl;
    return -1;
  }

  gz::msgs::Twist msg;
  // Prepare the message.
      msg.mutable_linear()->set_x(1.0);  // linear velocity in x-direction (m/s)
    msg.mutable_linear()->set_y(0.0);  // linear velocity in y-direction (m/s)
    msg.mutable_linear()->set_z(0.0);  // linear velocity in z-direction (m/s)

    msg.mutable_angular()->set_x(0.0);  // angular velocity around x-axis (rad/s)
    msg.mutable_angular()->set_y(0.0);  // angular velocity around y-axis (rad/s)
    msg.mutable_angular()->set_z(1.0);  // angular velocity around z-axis (rad/s)
  // Publish messages at 1Hz.
  while (!g_terminatePub)
  {
    if (!pub.Publish(msg))
      break;
