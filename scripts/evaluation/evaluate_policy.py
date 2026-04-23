import tyro

from dataclasses import dataclass
from droid.evaluation.policy_client import PolicyClient
from droid.robot_env import RobotEnv
from droid.trajectory_utils.misc import collect_trajectory

@dataclass
class Args:
    task: str
    policy: str
    policy_host: str = "0.0.0.0"
    policy_port: int = 8000
    horizon: int = 450
    save_dir: str = "evals"
    episodes: int = 20

def main(args: Args):
    # Make the robot env
    env = RobotEnv()
    print("Environment Ready...")

    # Connect to remote policy server
    policy = PolicyClient(
        host=args.policy_host,  # IP of the policy server
        port=args.policy_port,
        instruction=args.instruction,
    )
    print("Policy Connected...")

    # Use policy client for autonomous rollout:
    for i in range(args.episodes):
        print(f"Collecting Trajectory... {i+1}/{args.episodes}")
        collect_trajectory(
            env, 
            policy=policy, 
            horizon=args.horizon,
            save_filepath=f"{args.save_dir}/{args.task}/{args.policy}/{i:03d}.h5",
            save_raw_frames=True,
        )

if __name__ == "__main__":
    args = tyro.cli(Args)
    main(args)
