"""
三维向量数学库

提供三维向量的基本运算，包括:
- 向量加减乘除
- 点积和叉积
- 向量范数和归一化
- 向量间角度计算
- 旋转向量计算

使用示例:
    from lib.vector import Vector
    
    v1 = Vector(1, 0, 0)
    v2 = Vector(0, 1, 0)
    
    dot = Vector.dot(v1, v2)      # 点积
    cross = Vector.cross(v1, v2)  # 叉积
    angle = Vector.angle_between(v1, v2)  # 夹角
"""

import math
from typing import Union

class Vector:
    """
    三维向量类。
    
    属性:
        x: X 分量
        y: Y 分量
        z: Z 分量
    """
    __slots__ = ['x', 'y', 'z']
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def zero(self) -> bool:
        return self.x == 0 and self.y == 0 and self.z == 0
    
    def is_finite(self) -> bool:
        return math.isfinite(self.x) and math.isfinite(self.y) and math.isfinite(self.z)
    
    def valid(self) -> bool:
        return self.is_finite()
    
    def invalid(self) -> bool:
        return not self.valid()
    
    def invalidate(self) -> None:
        self.x = float('nan')
        self.y = float('nan')
        self.z = float('nan')
    
    def norm(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self) -> None:
        n = self.norm()
        if n > 0:
            self.x /= n
            self.y /= n
            self.z /= n
    
    def __add__(self, other: Union['Vector', int, float]) -> 'Vector':
        if isinstance(other, (int, float)):
            return Vector(self.x + other, self.y + other, self.z + other)
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __radd__(self, other: Union[int, float]) -> 'Vector':
        return self.__add__(other)
    
    def __sub__(self, other: Union['Vector', int, float]) -> 'Vector':
        if isinstance(other, (int, float)):
            return Vector(self.x - other, self.y - other, self.z - other)
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, other: Union['Vector', int, float]) -> 'Vector':
        if isinstance(other, (int, float)):
            return Vector(self.x * other, self.y * other, self.z * other)
        return Vector(self.x * other.x, self.y * other.y, self.z * other.z)
    
    def __rmul__(self, other: Union[int, float]) -> 'Vector':
        return self.__mul__(other)
    
    def __truediv__(self, other: Union['Vector', int, float]) -> 'Vector':
        if isinstance(other, (int, float)):
            return Vector(self.x / other, self.y / other, self.z / other)
        return Vector(self.x / other.x, self.y / other.y, self.z / other.z)
    
    def __neg__(self) -> 'Vector':
        return Vector(-self.x, -self.y, -self.z)
    
    def __iadd__(self, other: Union['Vector', int, float]) -> 'Vector':
        if isinstance(other, (int, float)):
            self.x += other
            self.y += other
            self.z += other
        else:
            self.x += other.x
            self.y += other.y
            self.z += other.z
        return self
    
    def __isub__(self, other: Union['Vector', int, float]) -> 'Vector':
        if isinstance(other, (int, float)):
            self.x -= other
            self.y -= other
            self.z -= other
        else:
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
        return self
    
    def __imul__(self, other: Union['Vector', int, float]) -> 'Vector':
        if isinstance(other, (int, float)):
            self.x *= other
            self.y *= other
            self.z *= other
        else:
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
        return self
    
    def __itruediv__(self, other: Union['Vector', int, float]) -> 'Vector':
        if isinstance(other, (int, float)):
            self.x /= other
            self.y /= other
            self.z /= other
        else:
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z
        return self
    
    def __eq__(self, other: object) -> bool:
        return self.x == other.x and self.y == other.y and self.z == other.z
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
    
    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y}, {self.z})"
    
    def copy(self) -> 'Vector':
        return Vector(self.x, self.y, self.z)
    
    @staticmethod
    def dot(a: 'Vector', b: 'Vector') -> float:
        return a.x * b.x + a.y * b.y + a.z * b.z
    
    @staticmethod
    def cross(a: 'Vector', b: 'Vector') -> 'Vector':
        return Vector(
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x
        )
    
    @staticmethod
    def angle_between(a: 'Vector', b: 'Vector') -> float:
        dot = Vector.dot(a, b)
        norm_a = a.norm()
        norm_b = b.norm()
        if norm_a == 0 or norm_b == 0:
            return 0.0
        cos_angle = max(-1.0, min(1.0, dot / (norm_a * norm_b)))
        return math.acos(cos_angle)
    
    @staticmethod
    def rotation_vector_between(a: 'Vector', b: 'Vector') -> 'Vector':
        direction = Vector.cross(a, b)
        if direction.zero():
            perp = Vector.cross(a, Vector(1, 0, 0))
            if perp.zero():
                perp = Vector.cross(a, Vector(0, 1, 0))
            return perp
        direction.normalize()
        angle = Vector.angle_between(a, b)
        return direction * angle
