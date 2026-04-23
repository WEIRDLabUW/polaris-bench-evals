import numpy as np
from openpi_client import image_tools
from openpi_client import websocket_client_policy

import droid.misc.parameters as params


class PolicyClient:
    """Policy client that connects to a remote openpi policy server via websocket.

    Implements the `forward(obs)` interface expected by `collect_trajectory`.
    Handles observation extraction, image resizing, action chunking, and gripper binarization.
    """

    def __init__(
        self,
        host: str,
        port: int = 8000,
        instruction: str = "",
        image_size: int = 224,
        open_loop_horizon: int = 8,
        left_camera_id: str = params.varied_camera_1_id,
        right_camera_id: str = "",
        wrist_camera_id: str = params.hand_camera_id,
        external_camera: str = "left",
        binarize_gripper: bool = True,
    ):
        self.policy = websocket_client_policy.WebsocketClientPolicy(host, port)
        self.instruction = instruction
        self.image_size = image_size
        self.open_loop_horizon = open_loop_horizon

        self.left_camera_id = left_camera_id
        self.right_camera_id = right_camera_id
        self.wrist_camera_id = wrist_camera_id
        self.external_camera = external_camera
        self.binarize_gripper = binarize_gripper

        self._action_chunk = None
        self._chunk_step = 0

    def _extract_observation(self, obs):
        """Extract and process images and state from a DROID observation dict."""
        image_obs = obs["image"]
        left_image, right_image, wrist_image = None, None, None

        for key in image_obs:
            if self.left_camera_id in key and "left" in key:
                left_image = image_obs[key]
            elif self.right_camera_id in key and "left" in key:
                right_image = image_obs[key]
            elif self.wrist_camera_id in key and "left" in key:
                wrist_image = image_obs[key]

        # Drop alpha channel and convert BGR -> RGB
        def process_img(img):
            if img is None:
                return None
            img = img[..., :3]
            img = img[..., ::-1]
            return img

        left_image = process_img(left_image)
        right_image = process_img(right_image)
        wrist_image = process_img(wrist_image)

        robot_state = obs["robot_state"]
        return {
            "left_image": left_image,
            "right_image": right_image,
            "wrist_image": wrist_image,
            "joint_position": np.array(robot_state["joint_positions"]),
            "gripper_position": np.array([robot_state["gripper_position"]]),
        }

    def forward(self, obs):
        """Return a single action. Queries the server when the current action chunk is exhausted."""
        # If we have actions left in the current chunk, use them
        if self._action_chunk is not None and self._chunk_step < self.open_loop_horizon:
            action = self._action_chunk[self._chunk_step]
            self._chunk_step += 1
            if self.binarize_gripper:
                action = self._binarize_gripper_action(action)
            return action

        # Otherwise, query the policy server for a new chunk
        extracted = self._extract_observation(obs)
        external_key = f"{self.external_camera}_image"
        sz = self.image_size

        request_data = {
            "observation/exterior_image_1_left": image_tools.resize_with_pad(extracted[external_key], sz, sz),
            "observation/wrist_image_left": image_tools.resize_with_pad(extracted["wrist_image"], sz, sz),
            "observation/joint_position": extracted["joint_position"],
            "observation/gripper_position": extracted["gripper_position"],
            "prompt": self.instruction,
        }

        self._action_chunk = self.policy.infer(request_data)["actions"]
        self._chunk_step = 1  # we're about to return index 0

        action = self._action_chunk[0]
        if self.binarize_gripper:
            action = self._binarize_gripper_action(action)
        return action

    @staticmethod
    def _binarize_gripper_action(action):
        gripper_val = 1.0 if action[-1] > 0.5 else 0.0
        return np.concatenate([action[:-1], [gripper_val]])

    def reset(self):
        """Reset the action chunk state between rollouts."""
        self._action_chunk = None
        self._chunk_step = 0
