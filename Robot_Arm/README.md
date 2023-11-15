# 📌 README.md

> ## _RobotArm_Project_ 🤖

---

**⭐︎ How to control?**

: You can select robot arm joint (from bottom 1,2,3) using number key 1, 2, 3.
Press the space key to hold the gripper and press again to stop.
play: If you press the direction key while holding the number key, you can rotate robot arm.

---

**⭐︎ Main idea**

: using Rmat function, you can rotate polygons.

```python
def Rmat(degree):
    rad = np.deg2rad(degree)
    c = np.cos(rad)
    s = np.sin(rad)
    R = np.array([[c, -s, 0],
                  [s,  c, 0], [0, 0, 1]])
    return R
```

: using Tmat function, you can move polygons.

```python
def Tmat(tx, ty):
    Translation = np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ])
    return Translation

```

---

youtube link
[![robotarm](http://img.youtube.com/vi/i2TLwd6HLls/0.jpg)](https://youtu.be/i2TLwd6HLls)
