from droid.controllers.oculus_controller import VRPolicy
from droid.evaluation.policy_client import PolicyClient
from droid.robot_env import RobotEnv
from droid.trajectory_utils.misc import collect_trajectory

# Make the robot env
env = RobotEnv()
controller = VRPolicy()

# Connect to remote policy server
policy = PolicyClient(
    host="0.0.0.0",  # IP of the policy server
    port=8000,
    instruction="pick up the object",
)

print("Ready")
# Use controller for teleoperation:
# collect_trajectory(env, controller=controller)

# Use policy client for autonomous rollout:
collect_trajectory(env, policy=policy, horizon=450)
