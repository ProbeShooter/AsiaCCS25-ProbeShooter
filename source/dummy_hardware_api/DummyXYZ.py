from typing import Optional


__all__ = [
    'DummyXYZ'
]


class DummyXYZ:
    def connect(self, port) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def move_to_xyz(self,
                    position_x: Optional[int],
                    position_y: Optional[int],
                    position_z: Optional[int],
                    velocity: int = -1,
                    block: bool = True
                    ) -> None:
        pass

    def set_params(self, max_pos_x, max_pos_y, max_pos_z, max_velocity) -> None:
        pass
    pass
