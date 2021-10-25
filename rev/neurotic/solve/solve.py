import torch
from torch import nn
import numpy as np
from functools import reduce
import base64


class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.stack = nn.Sequential(*([nn.Linear(8, 8, bias=False)] * 7))

    def forward(self, x):
        x = self.stack(x)
        return x


ct = b"1VfgPsBNALxwfdW9yUmwPpnI075HhKg9bD5gPDLvjL026ho/xEpQvU5D4L3mOso+KGS7vvpT5T0FeN284inWPXyjaj7oZgI8I7q5vTWhOj7yFEq+TtmsPaYN7jxytdC9cIGwPti6ALw28Pm9eFZ/PkVBV75iV/U9NoP4PDoFn72+rI8+HHZivMwJvr2s5IQ+nASFvhoW2j1+uHE98MbuvdSNsT4kzrK82BGLvRrikz6oU66+oCGCPajDmzyg7Q69OjiDPvQtnjxwWw2+IB9ZPmaCLb4Mwhc+LimEPXXBQL75OQ8/ulQUvZZMsr3iO88+ZHz3viUgLT2U/d68C2xYPQ=="

Y = np.reshape(np.frombuffer(base64.b64decode(ct), dtype=np.float32), (8, 8))

model = NeuralNetwork()
model.load_state_dict(torch.load("../src/model.pth"))

Ms = [x.weight.detach().numpy().T for x in model.stack]  # type: ignore
M = reduce(np.matmul, Ms)
X = np.matmul(Y, np.linalg.inv(M))
X = np.around(X)
print(X)
flag = bytes(int(x) for x in X.flatten())
print(flag)
