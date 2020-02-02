import subprocess


class K8s:
    """Interact with K8s resources"""

    def __init__(self):
        pass

    def __repr__(self):
        return f'Kubernetes'


def main():
    k8s = K8s()
    print(k8s)


if __name__ == '__main__':
    main()
