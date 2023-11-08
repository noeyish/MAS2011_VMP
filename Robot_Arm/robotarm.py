import pygame
import numpy as np

RED = (255, 0, 0)

FPS = 60   # frames per second

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800

pygame.display.set_caption("20221573_심하연_Robot Arm")


def Rmat(degree):
    rad = np.deg2rad(degree)
    c = np.cos(rad)
    s = np.sin(rad)
    R = np.array([[c, -s, 0],
                  [s,  c, 0], [0, 0, 1]])
    return R


def Tmat(tx, ty):
    Translation = np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ])
    return Translation


def draw(P, H, screen, outline_color=(100, 200, 200), fill_color=(200, 200, 200)):
    R = H[:2, :2]
    T = H[:2, 2]
    Ptransformed = P @ R.T + T
    pygame.draw.polygon(screen, fill_color, points=Ptransformed)


def main():
    pygame.init()  # initialize the engine

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    w = 200
    h = 20
    X = np.array([[0, 0], [w, 0], [w, h], [0, h]])
    B = np.array([[0, 0], [500, 0], [500, 40], [0, 40]])

    W = 40
    H = 10
    Y = np.array([[0, 0], [W, 0], [W, H], [0, H]])
    Y1 = np.array([[0, 0], [W, 0], [W, 0], [0, H]])
    Y2 = np.array([[0, 0], [0, 0], [W, H], [0, H]])

    position = [WINDOW_WIDTH/2, WINDOW_HEIGHT - 100]
    jointangle1 = 10
    jointangle2 = -10
    jointangle3 = 10

    done = False
    angle_increment = 1
    g_flag = 0  # gripper off
    g = 0

    font = pygame.font.Font(None, 36)
    text1 = font.render(
        "joint1: key1   joint2: key2   joint3: key3", True, (0, 0, 0))
    text2 = font.render("Rotate: <- -> key", True, (0, 0, 0))
    text3 = font.render("Grip: space key", True, (0, 0, 0))

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            if keys[pygame.K_RIGHT]:
                jointangle1 += angle_increment
            if keys[pygame.K_LEFT]:
                jointangle1 -= angle_increment
        elif keys[pygame.K_2]:
            if keys[pygame.K_RIGHT]:
                jointangle2 += angle_increment
            if keys[pygame.K_LEFT]:
                jointangle2 -= angle_increment
        elif keys[pygame.K_3]:
            if keys[pygame.K_RIGHT]:
                jointangle3 += angle_increment
            if keys[pygame.K_LEFT]:
                jointangle3 -= angle_increment

        if keys[pygame.K_SPACE]:
            if g_flag == 0:
                g = 10
                g_flag = 1
            else:
                g = 0
                g_flag = 0

        screen.fill((200, 254, 219))
        H0 = Tmat(position[0], position[1]) @ Tmat(0, -h)@Tmat(-200, 0)
        draw(B, H0, screen, None, (220, 220, 220))  # base

        H1 = H0 @ Tmat(w/2, 0)
        x, y = H1[0, 2], H1[1, 2]  # joint position
        H11 = H1 @ Rmat(-90) @ Tmat(0, -h/2)
        H12 = H11 @ Tmat(0, h/2) @ Rmat(jointangle1) @ Tmat(0, -h/2)
        draw(X, H12, screen, (0, 0, 200))
        pygame.draw.circle(screen, (200, 200, 200), (x, y), radius=10)

        H2 = H12 @ Tmat(w, 0) @ Tmat(0, h/2)  # joint 2
        x, y = H2[0, 2], H2[1, 2]
        H21 = H2 @ Rmat(jointangle2) @ Tmat(0, -h/2)
        H22 = H21 @ Tmat(0, h/2) @ Rmat(jointangle2) @ Tmat(0, -h/2)
        draw(X, H22, screen, None, (165, 165, 165))
        pygame.draw.circle(screen, (165, 165, 165), (x, y), radius=10)

        H3 = H22 @ Tmat(w, 0) @ Tmat(0, h/2)  # joint 2
        x, y = H3[0, 2], H3[1, 2]
        H31 = H3 @ Rmat(jointangle3) @ Tmat(0, -h/2)
        H32 = H31 @ Tmat(0, h/2) @ Rmat(jointangle3) @ Tmat(0, -h/2)
        draw(X, H32, screen, None, (135, 135, 135))
        pygame.draw.circle(screen, (135, 135, 135), (x, y), radius=10)

        G3 = H32 @ Tmat(w, 0) @ Tmat(0, h/2-20) @ Rmat(90)
        G31 = G3 @ Tmat(0, -h/2)
        G32 = G31 @ Tmat(0, h/2) @ Tmat(0, -h/2)
        draw(Y, G32, screen, None, (100, 100, 100))

        G1 = H32 @ Tmat(w+10, 0) @ Tmat(0, h+10)@Rmat(-g)
        G11 = G1 @ Tmat(0, -h/2)
        G12 = G11 @ Tmat(0, h/2) @ Tmat(0, -h/2)
        draw(Y1, G12, screen, None, (100, 100, 100))
        x, y = G1[0, 2], G1[1, 2]

        G2 = H32 @ Tmat(w+10, 0) @ Tmat(0, h/2-10)@Rmat(g)
        G21 = G2 @ Tmat(0, -h/2)
        G22 = G21 @ Tmat(0, h/2) @ Tmat(0, -h/2)
        draw(Y2, G22, screen, None, (100, 100, 100))

        screen.blit(text1, (10, 0))
        screen.blit(text2, (10, 30))
        screen.blit(text3, (10, 60))
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
