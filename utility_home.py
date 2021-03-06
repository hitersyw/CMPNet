import torch
from torch.autograd import Variable
import copy
import numpy as np
import time
def normalize(x, bound, time_flag=False):
    # normalize to -1 ~ 1  (bound can be a tensor)
    #return x
    time_0 = time.time()
    lower = np.array([-383.8, -371.47, -0.2, -1, -1, -1, -1])
    higher = np.array([325, 337.89, 142.33, 1, 1, 1, 1])
    bound = (higher - lower) / 2
    #print('before normalizing...')
    #print(x)
    if type(x) is not np.ndarray:
        bound = torch.from_numpy(bound).type(torch.FloatTensor)
        lower = torch.from_numpy(lower).type(torch.FloatTensor)
        higher = torch.from_numpy(higher).type(torch.FloatTensor)
        x_shape = x.size()
    else:
        x_shape = x.shape
    if len(x_shape) != 1:
        # then the proceding is obstacle
        # don't normalize obstacles
        # we assume the obstacle pcd has been normalized
        if len(x[0]) != len(bound):
            x[:,:-len(bound)] = (x[:,:-len(bound)]-lower) / bound - 1.0
            x[:,-len(bound):] = (x[:,-len(bound):]-lower) / bound - 1.0
            # normalize the quarternion part
            if type(x) is not np.ndarray:
                x[:,3:7] = x[:,3:7] / torch.norm(x[:,3:7], dim=1, keepdim=True)
                x[:,len(bound)+3:] = x[:,len(bound)+3:] / torch.norm(x[:,len(bound)+3:], dim=1, keepdim=True)
            else:
                x[:,3:7] = x[:,3:7] / np.linalg.norm(x[:,3:7], axis=1, keepdims=True)
                x[:,len(bound)+3:] = x[:,len(bound)+3:] / np.linalg.norm(x[:,len(bound)+3:], axis=1, keepdims=True)

        else:
            x = (x-lower) / bound - 1.0
            if type(x) is not np.ndarray:
                x[:,3:] = x[:,3:] / torch.norm(x[:,3:], dim=1, keepdim=True)
            else:
                x[:,3:] = x[:,3:] / np.linalg.norm(x[:,3:], axis=1, keepdims=True)

        #print('after normalizing...')
        #print(x[:,-2*len(bound):])
    else:
        #print('before normalizing...')
        #print(x)
        if len(x) == len(bound):
            x = (x - lower) / bound - 1.0
            if type(x) is not np.ndarray:
                x[3:] = x[3:] / torch.norm(x[3:], dim=0, keepdim=True)
            else:
                x[3:] = x[3:] / np.linalg.norm(x[3:], axis=0, keepdims=True)

        else:
            x[:-len(bound)] = (x[:-len(bound)]-lower) / bound - 1.0
            x[-len(bound):] = (x[-len(bound):]-lower) / bound - 1.0
            if type(x) is not np.ndarray:
                x[3:7] = x[3:7] / torch.norm(x[3:7], dim=0, keepdim=True)
                x[len(bound)+3:] = x[len(bound)+3:] / torch.norm(x[len(bound)+3:], dim=0, keepdim=True)
            else:
                x[3:7] = x[3:7] / np.linalg.norm(x[3:7], axis=0, keepdims=True)
                x[len(bound)+3:] = x[len(bound)+3:] / np.linalg.norm(x[len(bound)+3:], axis=0, keepdims=True)

        #print('after normalizing...')
        #print(x)
    if time_flag:
        return x, time.time() - time_0
    else:
        return x
def unnormalize(x, bound, time_flag=False):
    # from -1~1 to the actual bound
    # x only one dim
    #return x
    time_0 = time.time()
    lower = np.array([-383.8, -371.47, -0.2, -1, -1, -1, -1])
    higher = np.array([325, 337.89, 142.33, 1, 1, 1, 1])
    bound = (higher - lower) / 2
    # normalize quarternion
    if type(x) is not np.ndarray:
        bound = torch.from_numpy(bound).type(torch.FloatTensor)
        lower = torch.from_numpy(lower).type(torch.FloatTensor)
        higher = torch.from_numpy(higher).type(torch.FloatTensor)
        x_shape = x.size()
    else:
        x_shape = x.shape
    if len(x_shape) != 1:
        # then the proceding is obstacle
        # don't normalize obstacles
        if len(x[0]) != len(bound):
            x[:,:-len(bound)] = (x[:,:-len(bound)] + 1.0) * bound + lower
            x[:,-len(bound):] = (x[:,-len(bound):] + 1.0) * bound + lower
            # normalize quarternion
            if type(x) is not np.ndarray:
                x[:,3:7] = x[:,3:7] / torch.norm(x[:,3:7], dim=1, keepdim=True)
                x[:,len(bound)+3:] = x[:,len(bound)+3:] / torch.norm(x[:,len(bound)+3:], dim=1, keepdim=True)
            else:
                x[:,3:7] = x[:,3:7] / np.linalg.norm(x[:,3:7], axis=1, keepdims=True)
                x[:,len(bound)+3:] = x[:,len(bound)+3:] / np.linalg.norm(x[:,len(bound)+3:], axis=1, keepdims=True)

        else:
            # normalize quarternion
            x = (x + 1.0) * bound + lower
            if type(x) is not np.ndarray:
                x[:,3:] = x[:,3:] / torch.norm(x[:,3:], dim=1, keepdim=True)
            else:
                x[:,3:] = x[:,3:] / np.linalg.norm(x[:,3:], axis=1, keepdims=True)
    else:
        #print('before unnormalizing...')
        #print(x)
        if len(x) == len(bound):
            x = (x + 1.0) * bound + lower
            if type(x) is not np.ndarray:
                x[3:] = x[3:] / torch.norm(x[3:], dim=0, keepdim=True)
            else:
                x[3:] = x[3:] / np.linalg.norm(x[3:], axis=0, keepdims=True)
        else:
            x[:-len(bound)] = (x[:-len(bound)] + 1.0) * bound + lower
            x[-len(bound):] = (x[-len(bound):] + 1.0) * bound + lower
            # normalize quarternion
            if type(x) is not np.ndarray:
                x[3:7] = x[3:7] / torch.norm(x[3:7], dim=0, keepdim=True)
                x[len(bound)+3:] = x[len(bound)+3:] / torch.norm(x[len(bound)+3:], dim=0, keepdim=True)
            else:
                x[3:7] = x[3:7] / np.linalg.norm(x[3:7], axis=0, keepdims=True)
                x[len(bound)+3:] = x[len(bound)+3:] / np.linalg.norm(x[len(bound)+3:], axis=0, keepdims=True)
        #print('after unnormalizing...')
        #print(x)
    if time_flag:
        return x, time.time() - time_0
    else:
        return x
