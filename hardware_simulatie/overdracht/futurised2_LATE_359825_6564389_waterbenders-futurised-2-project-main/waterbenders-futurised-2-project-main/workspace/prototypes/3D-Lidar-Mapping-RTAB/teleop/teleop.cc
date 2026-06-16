#include <iostream>
#include <thread>
#include <chrono>
#include <csignal>
#include <atomic>

#include <SDL2/SDL.h>

#include <gz/transport.hh>
#include <gz/msgs/twist.pb.h>

std::atomic<bool> running{true};

void SignalHandler(int)
{
  running = false;
}

int main()
{
  std::signal(SIGINT, SignalHandler);
  std::signal(SIGTERM, SignalHandler);

  if (SDL_Init(SDL_INIT_VIDEO) != 0)
  {
    std::cerr << "SDL_Init failed: " << SDL_GetError() << std::endl;
    return 1;
  }

  SDL_Window *window = SDL_CreateWindow(
      "Teleop",
      SDL_WINDOWPOS_CENTERED,
      SDL_WINDOWPOS_CENTERED,
      400, 200,
      SDL_WINDOW_SHOWN);

  if (!window)
  {
    std::cerr << "SDL_CreateWindow failed: " << SDL_GetError() << std::endl;
    SDL_Quit();
    return 1;
  }

  gz::transport::Node node;
  auto pub = node.Advertise<gz::msgs::Twist>("/cmd_vel");

  if (!pub)
  {
    std::cerr << "Failed to advertise /cmd_vel" << std::endl;
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 1;
  }

  constexpr double forwardSpeed = 1.0;
  constexpr double reverseSpeed = -1.0;
  constexpr double leftSteer = 0.8;
  constexpr double rightSteer = -0.8;

  // Small motion when only turning left/right
  constexpr double turnInPlaceCreep = 0.15;

  std::cout << "Teleop started.\n";
  std::cout << "Use arrow keys. Space = stop. Close window or Ctrl+C to quit.\n";

  while (running)
  {
    SDL_Event event;
    while (SDL_PollEvent(&event))
    {
      if (event.type == SDL_QUIT)
        running = false;
    }

    SDL_PumpEvents();
    const Uint8 *keys = SDL_GetKeyboardState(nullptr);

    const bool up    = keys[SDL_SCANCODE_UP];
    const bool down  = keys[SDL_SCANCODE_DOWN];
    const bool left  = keys[SDL_SCANCODE_LEFT];
    const bool right = keys[SDL_SCANCODE_RIGHT];
    const bool space = keys[SDL_SCANCODE_SPACE];

    double linear = 0.0;
    double angular = 0.0;

    // Forward / backward
    if (up)
      linear = forwardSpeed;
    else if (down)
      linear = reverseSpeed;

    // Steering
    if (left)
      angular = leftSteer;
    else if (right)
      angular = rightSteer;

    // Left/right only: tight turning behavior
    if (!up && !down)
    {
      if (left)
      {
        linear = turnInPlaceCreep;
        angular = leftSteer;
      }
      else if (right)
      {
        linear = turnInPlaceCreep;
        angular = rightSteer;
      }
    }

    // Stop
    if (space)
    {
      linear = 0.0;
      angular = 0.0;
    }

    gz::msgs::Twist msg;
    msg.mutable_linear()->set_x(linear);
    msg.mutable_linear()->set_y(0.0);
    msg.mutable_linear()->set_z(0.0);
    msg.mutable_angular()->set_x(0.0);
    msg.mutable_angular()->set_y(0.0);
    msg.mutable_angular()->set_z(angular);

    pub.Publish(msg);

    std::this_thread::sleep_for(std::chrono::milliseconds(20));
  }

  gz::msgs::Twist stop;
  stop.mutable_linear()->set_x(0.0);
  stop.mutable_angular()->set_z(0.0);
  pub.Publish(stop);

  SDL_DestroyWindow(window);
  SDL_Quit();
  return 0;
}