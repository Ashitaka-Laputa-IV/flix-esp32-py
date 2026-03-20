"""
四元数旋转库

提供四元数的基本运算，用于表示和计算三维旋转:
- 从欧拉角、轴角、旋转向量创建四元数
- 四元数乘法 (旋转组合)
- 向量旋转
- 转换为欧拉角

使用示例:
    from lib.quaternion import Quaternion
    from lib.vector import Vector
    
    # 从欧拉角创建 (roll, pitch, yaw)
    q = Quaternion.from_euler(Vector(0.1, 0.2, 0.3))
    
    # 旋转向量
    v = Vector(0, 0, 1)
    rotated = Quaternion.rotate_vector(v, q)
    
    # 获取欧拉角
    euler = q.to_euler()
"""

import math
from typing import Union
from .vector import Vector

class Quaternion:
    """
    四元数类，用于表示三维旋转。
    
    属性:
        w: 标量分量
        x: X 向量分量
        y: Y 向量分量
        z: Z 向量分量
    """
    __slots__ = ['w', 'x', 'y', 'z']
    
    def __init__(self, w: float = 1.0, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.w = float(w)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    @staticmethod
    def from_axis_angle(axis: 'Vector', angle: float) -> 'Quaternion':
        half_angle = angle * 0.5
        sin2 = math.sin(half_angle)
        cos2 = math.cos(half_angle)
        n = axis.norm()
        if n == 0:
            return Quaternion()
        sin_norm = sin2 / n
        return Quaternion(cos2, axis.x * sin_norm, axis.y * sin_norm, axis.z * sin_norm)
    
    @staticmethod
    def from_rotation_vector(rotation: 'Vector') -> 'Quaternion':
        if rotation.zero():
            return Quaternion()
        return Quaternion.from_axis_angle(rotation, rotation.norm())
    
    @staticmethod
    def from_euler(euler: 'Vector') -> 'Quaternion':
        cx = math.cos(euler.x / 2)
        cy = math.cos(euler.y / 2)
        cz = math.cos(euler.z / 2)
        sx = math.sin(euler.x / 2)
        sy = math.sin(euler.y / 2)
        sz = math.sin(euler.z / 2)
        
        return Quaternion(
            cx * cy * cz + sx * sy * sz,
            sx * cy * cz - cx * sy * sz,
            cx * sy * cz + sx * cy * sz,
            cx * cy * sz - sx * sy * cz
        )
    
    @staticmethod
    def from_between_vectors(u: 'Vector', v: 'Vector') -> 'Quaternion':
        dot = u.x * v.x + u.y * v.y + u.z * v.z
        w1 = u.y * v.z - u.z * v.y
        w2 = u.z * v.x - u.x * v.z
        w3 = u.x * v.y - u.y * v.x
        
        ret = Quaternion(
            dot + math.sqrt(dot * dot + w1 * w1 + w2 * w2 + w3 * w3),
            w1, w2, w3
        )
        ret.normalize()
        return ret
    
    def is_finite(self) -> bool:
        return all(math.isfinite(v) for v in [self.w, self.x, self.y, self.z])
    
    def valid(self) -> bool:
        return self.is_finite()
    
    def invalid(self) -> bool:
        return not self.valid()
    
    def invalidate(self) -> None:
        self.w = float('nan')
        self.x = float('nan')
        self.y = float('nan')
        self.z = float('nan')
    
    def norm(self) -> float:
        return math.sqrt(self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self) -> None:
        n = self.norm()
        if n > 0:
            self.w /= n
            self.x /= n
            self.y /= n
            self.z /= n
    
    def to_axis_angle(self) -> tuple['Vector', float]:
        angle = math.acos(min(1.0, max(-1.0, self.w))) * 2
        s = math.sin(angle / 2)
        if abs(s) < 1e-10:
            return Vector(0, 0, 0), angle
        axis = Vector(self.x / s, self.y / s, self.z / s)
        return axis, angle
    
    def to_rotation_vector(self) -> 'Vector':
        if self.w == 1 and self.x == 0 and self.y == 0 and self.z == 0:
            return Vector(0, 0, 0)
        axis, angle = self.to_axis_angle()
        return axis * angle
    
    def to_euler(self) -> 'Vector':
        sqx = self.x * self.x
        sqy = self.y * self.y
        sqz = self.z * self.z
        sqw = self.w * self.w
        
        sarg = -2 * (self.x * self.z - self.w * self.y) / (sqx + sqy + sqz + sqw)
        
        if sarg <= -0.99999:
            euler = Vector(0, -0.5 * math.pi, -2 * math.atan2(self.y, self.x))
        elif sarg >= 0.99999:
            euler = Vector(0, 0.5 * math.pi, 2 * math.atan2(self.y, self.x))
        else:
            euler = Vector(
                math.atan2(2 * (self.y * self.z + self.w * self.x), sqw - sqx - sqy + sqz),
                math.asin(max(-1.0, min(1.0, sarg))),
                math.atan2(2 * (self.x * self.y + self.w * self.z), sqw + sqx - sqy - sqz)
            )
        return euler
    
    def get_roll(self) -> float:
        return self.to_euler().x
    
    def get_pitch(self) -> float:
        return self.to_euler().y
    
    def get_yaw(self) -> float:
        return self.to_euler().z
    
    def set_roll(self, roll: float) -> None:
        euler = self.to_euler()
        q = Quaternion.from_euler(Vector(roll, euler.y, euler.z))
        self.w, self.x, self.y, self.z = q.w, q.x, q.y, q.z
    
    def set_pitch(self, pitch: float) -> None:
        euler = self.to_euler()
        q = Quaternion.from_euler(Vector(euler.x, pitch, euler.z))
        self.w, self.x, self.y, self.z = q.w, q.x, q.y, q.z
    
    def set_yaw(self, yaw: float) -> None:
        euler = self.to_euler()
        q = Quaternion.from_euler(Vector(euler.x, euler.y, yaw))
        self.w, self.x, self.y, self.z = q.w, q.x, q.y, q.z
    
    def __mul__(self, other: 'Quaternion') -> 'Quaternion':
        if isinstance(other, Quaternion):
            return Quaternion(
                self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,
                self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
                self.w * other.y + self.y * other.w + self.z * other.x - self.x * other.z,
                self.w * other.z + self.z * other.w + self.x * other.y - self.y * other.x
            )
        return NotImplemented
    
    def __eq__(self, other: object) -> bool:
        return self.w == other.w and self.x == other.x and self.y == other.y and self.z == other.z
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
    
    def __repr__(self) -> str:
        return f"Quaternion({self.w}, {self.x}, {self.y}, {self.z})"
    
    def copy(self) -> 'Quaternion':
        return Quaternion(self.w, self.x, self.y, self.z)
    
    def inversed(self) -> 'Quaternion':
        norm_sq_inv = 1.0 / (self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z)
        return Quaternion(
            self.w * norm_sq_inv,
            -self.x * norm_sq_inv,
            -self.y * norm_sq_inv,
            -self.z * norm_sq_inv
        )
    
    def conjugate(self, v: 'Vector') -> 'Vector':
        qv = Quaternion(0, v.x, v.y, v.z)
        res = self * qv * self.inversed()
        return Vector(res.x, res.y, res.z)
    
    def conjugate_inversed(self, v: 'Vector') -> 'Vector':
        qv = Quaternion(0, v.x, v.y, v.z)
        res = self.inversed() * qv * self
        return Vector(res.x, res.y, res.z)
    
    @staticmethod
    def rotate(a: 'Quaternion', b: 'Quaternion', normalize: bool = True) -> 'Quaternion':
        rotated = a * b
        if normalize:
            rotated.normalize()
        return rotated
    
    @staticmethod
    def rotate_vector(v: 'Vector', q: 'Quaternion') -> 'Vector':
        return q.conjugate_inversed(v)
    
    @staticmethod
    def between(a: 'Quaternion', b: 'Quaternion', normalize: bool = True) -> 'Quaternion':
        q = a * b.inversed()
        if normalize:
            q.normalize()
        return q
