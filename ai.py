import tensorflow as tf
import numpy as np
import os

from state import State, Action

state_size = 6
action_size = 4

# Define the Q-network
if os.path.isfile("/kaggle/working/model.h5"):
    model = tf.keras.models.load_model("/kaggle/working/model.h5")
elif os.path.isfile("/kaggle/input/trackgame/model.h5"):
    model = tf.keras.models.load_model("/kaggle/input/trackgame/model.h5")
else:
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(24, activation='relu', input_shape=(state_size,)),
        tf.keras.layers.Dense(24, activation='relu'),
        tf.keras.layers.Dense(action_size, activation='linear')
    ])

# Define the optimizer and loss function
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
loss_fn = tf.keras.losses.MeanSquaredError()

# Hyperparameters
gamma = 0.95  # Discount factor
epsilon = 1.0  # Exploration rate
epsilon_min = 0.01
epsilon_decay = 0.995
num_episodes = 1000

total_reward = 0

def get_ai_action(state: State) -> Action:
    global total_reward
    total_reward += state.reward

    # Numpy needs to expand array dimensions
    features = np.expand_dims(state.get_ai_features(), axis=0)

    # Use target Q-value for prediction to update Q table and gradients in model
    prediction = model.predict(features)
    target = state.reward + gamma * np.max(prediction)

    with tf.GradientTape() as tape:
        Q_values = model(features)
        loss = tf.reduce_mean(tf.square(target - Q_values))
    
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))

    # Random chance to take random action
    if np.random.rand() <= epsilon:
        action_index = np.random.randint(0, action_size)
    else:
        action_index = np.argmax(prediction)
    
    return state.actions[action_index]

def get_total_reward():
    return total_reward

def save_model():
    model.save("/kaggle/working/model.h5")