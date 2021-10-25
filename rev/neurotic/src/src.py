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


device = "cuda" if torch.cuda.is_available() else "cpu"

model = NeuralNetwork().to(device)
torch.save(model.state_dict(), "model.pth")

flag = b"buckeye{w41t_1ts_4ll_m4tr1x_mult1pl1cat10n????_4lwy4y5_h4s_b33n}"
assert len(flag) == 64
X = np.reshape(list(flag), (8, 8)).astype(np.float32)

Xt = torch.from_numpy(X).to(device)
Y = model(Xt).detach().numpy()

print(base64.b64encode(Y).decode())

# Do not distribute this to players
Ms = [x.weight.detach().numpy().T for x in model.stack]  # type: ignore
M = reduce(np.matmul, Ms)
print(np.matmul(X, M))
print("---")
print(Y)
assert np.allclose(np.matmul(X, M), Y)
