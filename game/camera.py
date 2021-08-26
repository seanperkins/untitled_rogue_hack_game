

class Camera:
    """
    Camera class.
    """

    def __init__(self, width, height):
        """
        Initialize the camera.
        :param width: Width of the camera.
        :param height: Height of the camera.
        """
        self.width = width - 2
        self.height = height - 2
        self.x = 0
        self.y = 0
        self.map_width = 0
        self.map_height = 0

        # Used to determine how many tiles over the camera is positioned
        self.screen_offset_x = 0
        self.screen_offset_y = 0

    def center_on(self, x, y):
        """
        Center the camera on a position.
        :param x: X position to center on.
        :param y: Y position to center on.
        """
        new_x = int(x - self.width / 2)
        if new_x > 0 and new_x < self.width:
            self.x = new_x
        elif new_x < 0:
            self.x = 0
        elif new_x + self.width > self.map_width:
            self.x = self.map_width - self.width

        new_y = int(y - self.height / 2)
        if new_y > 0 and new_y < self.height:
            self.y = new_y
        elif new_y < 0:
            self.y = 0
        elif new_y + self.height > self.map_height:
            self.y = self.map_height - self.height

    def move(self, x, y):
        """
        Move the camera.
        :param x: Change in X position.
        :param y: Change in Y position.
        """
        self.x += x
        self.y += y

    def set_position(self, x, y):
        """
        Set the camera position.
        :param x: X position to set to.
        :param y: Y position to set to.
        """
        self.x = x
        self.y = y

    def to_camera_coordinates(self, x, y):
        """
        Convert coordinates to camera coordinates.
        :param x: X position.
        :param y: Y position.
        :return: Converted X position.
        :return: Converted Y position.
        """
        adjusted_x = self.x - \
            self.screen_offset_x + x
        adjusted_y = self.y - \
            self.screen_offset_y + y

        if (x < 0 or y < 0 or x >= self.width or y >= self.height):
            return (None, None)  # if it's outside the view, return nothing

        return (adjusted_x, adjusted_y)
