import keras
from keras.models import Model, Sequential
from keras.layers import Dense, Activation, Input, LSTM, Permute, Reshape, Masking, TimeDistributed, MaxPooling1D, Flatten, Bidirectional
from keras.layers.merge import *
from keras.layers import Lambda
from keras.layers import Dropout
from keras.layers import concatenate, maximum, dot, average
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import LeakyReLU, PReLU, ELU
from keras.layers import Conv1D, GlobalMaxPooling1D, Conv2D, UpSampling2D, Conv2DTranspose, MaxPooling2D
from keras.layers.merge import *
from keras.optimizers import *
from keras.regularizers import *

def make_generator_mlp( GAN_noise_size, GAN_output_size ):
   # Build Generative model ...

   G_input = Input( shape=(GAN_noise_size,) )

   G = Dense( 64, kernel_initializer='glorot_normal' )(G_input)
   G = Activation('tanh')(G)
   G = BatchNormalization(momentum=0.8)(G) #0.8

   G = Dense( 32 )(G)
   G = Activation('tanh')(G)
   G = BatchNormalization(momentum=0.8)(G) #0.8

   G = Dense( 16 )(G)
   G = Activation('tanh')(G)

   G = Dense( GAN_output_size, activation="tanh" )(G)

   generator = Model( G_input, G )

   return generator

#~~~~~~~~~~~~~~~~~~~~~~

def make_discriminator_mlp( GAN_output_size ):
   # Build Discriminative model ...
   inshape = ( n_features, )
   D_input = Input( shape=inshape, name='D_input' )

   D = Dense( 64 )(D_input)

   D = Activation('tanh')(D)
   D = BatchNormalization(momentum=0.99)(D) # 0.8

   D = Dense( 32 )(D)
   D = Activation('tanh')(D)
   D = BatchNormalization(momentum=0.99)(D)
   
   D = Dense( 16 )(D)
   D = Activation('tanh')(D)
   #D = BatchNormalization(momentum=0.99)(D)

   #D = Dense( 8 )(D)
   #D = Activation('tanh')(D)
   #D = BatchNormalization(momentum=0.99)(D)
   
   #D = Dense( 4 )(D)
   #D = Activation('elu')(D)

   #D_output = Dense( 2, activation="softmax")(D)
   D_output = Dense( 1, activation="sigmoid")(D)
   discriminator = Model( D_input, D_output )
   #discriminator.compile( loss='categorical_crossentropy', optimizer=dopt )
   
   return discriminator


##########################


def make_generator_cnn( GAN_noise_size, GAN_output_size ):
   # Build Generative model ...
   
   G_input = Input( shape=(GAN_noise_size,) )
   
   G = Dense( 64, kernel_initializer='glorot_uniform' )(G_input)
   G = Activation('tanh')(G)
   G = BatchNormalization(momentum=0.8)(G)
   
   G = Reshape( [ 8, 8, 1 ] )(G) #default: channel last

   G = Conv2D( filters=32, kernel_size=3, padding="same" )(G)
   G = Activation('tanh')(G)

   G = Conv2D( filters=64, kernel_size=3, padding="same" )(G)
   G = Activation('tanh')(G)

   # Upsample to make the input larger
   #G = UpSampling2D(size=2)(G)
   #G = Conv2D( filters=8, kernel_size=3, strides=1, padding='same' )(G)
   # same thing, quicker but introduces artifacts:
   #G = Conv2DTranspose( filters=4, kernel_size=4, strides=2, padding='same')(G)
   #G = Activation('tanh')(G)
   #G = BatchNormalization(momentum=0.99)(G)

   #G = Conv2D( filters=8, kernel_size=3, padding="same" )(G)
   #G = Activation('tanh')(G)
   #G = BatchNormalization(momentum=0.99)(G)

   
   #G = Conv2D( filters=16, kernel_size=2, padding="same" )(G)
   #G = Activation('tanh')(G)
   #G = BatchNormalization(momentum=0.99)(G)
   
   #G = Conv2D( filters=16, kernel_size=4, padding="same" )(G)
   #G = Activation('tanh')(G)
   #G = BatchNormalization(momentum=0.8)(G)
   
   #G = MaxPooling2D( (2,2) )(G)
   
   G = Flatten()(G)
   G = Dense( GAN_output_size, activation="tanh" )(G)
   #G = Dropout(0.2)(G)
   
   generator = Model( G_input, G )
   
   return generator

#~~~~~~~~~~~~~~~~~~~~~~

def make_discriminator_cnn( GAN_output_size ):
   # Build Discriminative model ...
    print "DEBUG: discriminator: input features:", GAN_output_size
    
    inshape = ( GAN_output_size, )
    D_input = Input( shape=inshape, name='D_input' )

    #D = Reshape( (-1,n_fso_max, n_features_per_fso) )(D_input)
    D = Dense(256)(D_input)
    D = Reshape( (1,16,16) )(D)
   
    D = Conv2D( 128, 1, strides=1 )(D)
    D = Activation('tanh')(D)

    D = Conv2D( 64, 1, strides=1 )(D)
    D = Activation('tanh')(D)

    D = Flatten()(D)
    D = Dropout(0.2)(D)
   
    #D_output = Dense( 2, activation="softmax")(D)
    D_output = Dense( 1, activation="sigmoid")(D)
    discriminator = Model( D_input, D_output )
   
    return discriminator


##########################


def make_generator_rnn( GAN_noise_size, GAN_output_size ):

   G_input = Input( shape=(GAN_noise_size,) )

   G = Dense( 128, kernel_initializer='glorot_normal' )(G_input)
   G = Activation('tanh')(G)
   G = BatchNormalization(momentum=0.99)(G) #0.8

   G = Reshape( (32,4) )(G)

   #G = Bidirectional( LSTM( 32, return_sequences=True  ) )(G)
   #G = Bidirectional( LSTM( 8, return_sequences=True ) )(G)
   G = LSTM( 32, return_sequences=True )(G)
   G = LSTM( 16, return_sequences=False )(G) #kernel_regularizer=regularizers.l2(0.01)
   G = Activation('tanh')(G)

   G = Dense( GAN_output_size, activation="tanh" )(G)

   generator = Model( G_input, G )

   return generator

#~~~~~~~~~~~~~~~~~~~~~~



def make_discriminator_rnn( GAN_output_size ):

   inshape = ( n_features, )
   D_input = Input( shape=inshape, name='D_input' )
   
   D = Dense( 128, kernel_initializer='glorot_normal' )(D_input)
   D = Activation('tanh')(D)
   D = Reshape( (16,8) )(D)

   #D = Bidirectional( LSTM( 16, return_sequences=True  ) )(D)
   
   D = Bidirectional( LSTM( 8, return_sequences=False ) )(D)
   D = Activation('tanh')(D)

    #D_output = Dense( 2, activation="softmax")(D)
   D_output = Dense( 1, activation="sigmoid")(D)
   discriminator = Model( D_input, D_output )
   #discriminator.compile( loss='categorical_crossentropy', optimizer=dopt )
   
   return discriminator


##########################