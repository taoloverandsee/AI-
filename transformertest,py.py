#transformert原理实现测试
import  torch
import torch.nn as nn
import torch.nn.functional as F
class PositionsEncoding(nn.Model):
    def __init__(self):
        pass
    #位置编码模块
    def forward(self,x):
        pass
#多头注意模块
class MultiHeadAttention(nn.Module):
    def forward(self,query,key,value,mask):
        pass


#位置前馈网络模块
class PositionalWiseFeedForward(nn.Module):
    def forward(self,x):
        pass



#编码器
class EncoderLayer(nn.Module):
    def __init__(self,d_model,number_heads,d_ff,dropout):
        super(EncoderLayer, self).__init__()
        self.self_attn=MultiHeadAttention()
        self.pos_encoding=PositionalWiseFeedForward()
        self.norm1=nn.LayerNorm(d_model)
        self.norm2= nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

#解码器

