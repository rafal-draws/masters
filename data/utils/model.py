from torch import nn
import torch.nn.functional as F

class AudioCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv1d(1, 16, kernel_size=5, stride=1, padding=2)
        self.pool1 = nn.MaxPool1d(4)

        self.conv2 = nn.Conv1d(16, 32, kernel_size=5, stride=1, padding=2)
        self.pool2 = nn.AdaptiveAvgPool1d(1)  

        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(32, 5)

    def forward(self, x):
        x = self.pool1(F.relu(self.conv1(x)))  # (B, 16, ~5512)
        x = self.pool2(F.relu(self.conv2(x)))  # (B, 32, 1)
        x = x.view(x.size(0), -1)              # (B, 32)
        x = self.dropout(x)
        return self.fc(x)