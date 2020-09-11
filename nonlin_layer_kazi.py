# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 17:33:48 2020

@author: Shounak
"""


import tensorflow as tf
from tensorflow.keras.layers import Layer
import itertools


class NONLIN_Layer(Layer):
    
    def __init__(self,TAKE_REPEATING_PRODUCTS,upto_how_many_degrees,initial_endmembers):
        
        self.initial_endmembers_init = initial_endmembers
        self.initial_endmembers_shape = initial_endmembers.shape
        self.TAKE_REPEATING_PRODUCTS = TAKE_REPEATING_PRODUCTS
        self.upto_how_many_degrees = upto_how_many_degrees
        
        super(NONLIN_Layer, self).__init__()
        
    def build(self, input_shape):
        
        self.linear_endmembers = self.add_weight("linear_endmembers", shape = self.initial_endmembers_shape,initializer=tf.constant_initializer(self.initial_endmembers_init))
        
        
        num = 0
        
        for i in range(2,self.upto_how_many_degrees+1):
            if (self.TAKE_REPEATING_PRODUCTS==1):        
                num += len(list((itertools.product(list(range(self.initial_endmembers_shape[0])), repeat=i))))
            else: num += len(list((itertools.combinations(list(range(self.initial_endmembers_shape[0])), i))))
            
            
        self.scaling_values = self.add_weight("scaling_factors", shape = (num,), initializer=tf.keras.initializers.Ones())
        
        
        
        super().build(input_shape)

    
    def call(self, x):
        
        num_classes = self.initial_endmembers_shape[0]
        classes = list(range(num_classes))
        
        pairs=[]
        for i in range(2,self.upto_how_many_degrees+1):    
        
            if (self.TAKE_REPEATING_PRODUCTS==1):
                 pairs += list(itertools.product(classes,repeat = i))
            else: pairs += list(itertools.combinations(classes, i))    
        
        E = tf.pad(self.linear_endmembers, ((0,len(pairs)),(0,0)), 'constant', constant_values=(0))
        mask = []
        
        for i in range(len(pairs)):
    
            pair = pairs[i]
            endmember_cross_product = tf.ones(E.shape[1])
            for k in range(len(pair)): 
                endmember_cross_product = tf.math.multiply(endmember_cross_product,E[pair[k],:])
                
            mask.append(self.scaling_values[i] * endmember_cross_product)
            
        mask_tf = tf.convert_to_tensor(mask)
        mask_tf = tf.pad(mask_tf, ((num_classes,0),(0,0)), 'constant', constant_values=(0))
        new_E = E + mask_tf
        
        return tf.matmul(x,new_E)
        
    
    def compute_output_shape(self, input_shape):
        return (input_shape[0],self.initial_endmembers_shape[1])