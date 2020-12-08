import base64
import cv2
import time
from io import BytesIO
from tensorflow import keras
from PIL import Image
from pymongo import MongoClient
import tensorflow as tf
import face_recognition
import numpy as np

# mongodb connection
conn = MongoClient('mongodb://root:123@localhost:27017/')
db = conn.myface  # Connect to mydb database. If not, it will be created automatically
user_face = db.user_face  # Use test_ Set collection. If not, it will be created automatically
face_images = db.face_images

lables = []
datas = []
INPUT_NODE = 128
LATER1_NODE = 200
OUTPUT_NODE = 0
TRAIN_DATA_SIZE = 0
TEST_DATA_SIZE = 0


def generateds():
    get_out_put_node()
    train_x, train_y, test_x, test_y = np.array(datas), np.array(lables), np.array(datas), np.array(lables)
    return train_x, train_y, test_x, test_y


def get_out_put_node():
    for item in face_images.find():
        lables.append(item['user_id'])
        datas.append(item['face_encoding'])
    OUTPUT_NODE = len(set(lables))
    TRAIN_DATA_SIZE = len(lables)
    TEST_DATA_SIZE = len(lables)
    return OUTPUT_NODE, TRAIN_DATA_SIZE, TEST_DATA_SIZE


# Face information verification
def predict_image(image):
    model = tf.keras.models.load_model('face_model.h5', compile=False)
    face_encode = face_recognition.face_encodings(image)
    result = []
    for j in range(len(face_encode)):
        predictions1 = model.predict(np.array(face_encode[j]).reshape(1, 128))
        print(predictions1)
        if np.max(predictions1[0]) > 0.90:
            print(np.argmax(predictions1[0]).dtype)
            pred_user = user_face.find_one({'id': int(np.argmax(predictions1[0]))})
            print('%d face is %s' % (j + 1, pred_user['user_name']))
            result.append(pred_user['user_name'])
    return result


# Save face information
def save_face(pic_path, uid):
    image = face_recognition.load_image_file(pic_path)
    face_encode = face_recognition.face_encodings(image)
    print(face_encode[0].shape)
    if (len(face_encode) == 1):
        face_image = {
            'user_id': uid,
            'face_encoding': face_encode[0].tolist()
        }
        face_images.insert_one(face_image)


# Training face information
def train_face():
    train_x, train_y, test_x, test_y = generateds()
    dataset = tf.data.Dataset.from_tensor_slices((train_x, train_y))
    dataset = dataset.batch(32)
    dataset = dataset.repeat()
    OUTPUT_NODE, TRAIN_DATA_SIZE, TEST_DATA_SIZE = get_out_put_node()
    model = keras.Sequential([
        keras.layers.Dense(128, activation=tf.nn.relu),
        keras.layers.Dense(128, activation=tf.nn.relu),
        keras.layers.Dense(OUTPUT_NODE, activation=tf.nn.softmax)
    ])

    model.compile(optimizer=tf.compat.v1.train.AdamOptimizer(),
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    steps_per_epoch = 30
    if steps_per_epoch > len(train_x):
        steps_per_epoch = len(train_x)
    model.fit(dataset, epochs=10, steps_per_epoch=steps_per_epoch)

    model.save('face_model.h5')


def register_face(user):
    if user_face.find({"user_name": user}).count() > 0:
        print("User already exists")
        return
    video_capture = cv2.VideoCapture(0)
    # In mongodb, sort() method is used to sort the data.
    # The sort() method can specify the sorting fields through parameters,
    # and use 1 and - 1 to specify the sorting method, where 1 is ascending and - 1 is descending.
    finds = user_face.find().sort([("id", -1)]).limit(1)
    uid = 0
    if finds.count() > 0:
        uid = finds[0]['id'] + 1
    print(uid)
    user_info = {
        'id': uid,
        'user_name': user,
        'create_time': time.time(),
        'update_time': time.time()
    }
    user_face.insert_one(user_info)

    while 1:
        # Get a frame of video
        ret, frame = video_capture.read()
        # window display
        cv2.imshow('Video', frame)
        # After adjusting the angle, take 5 pictures in succession
        if cv2.waitKey(1) & 0xFF == ord('q'):
            for i in range(1, 6):
                cv2.imwrite('Myface{}.jpg'.format(i), frame)
                with open('Myface{}.jpg'.format(i), "rb")as f:
                    img = f.read()
                    img_data = BytesIO(img)
                    im = Image.open(img_data)
                    im = im.convert('RGB')
                    imgArray = np.array(im)
                    faces = face_recognition.face_locations(imgArray)
                    save_face('Myface{}.jpg'.format(i), uid)
            break

    train_face()
    video_capture.release()
    cv2.destroyAllWindows()


def rec_face():
    video_capture = cv2.VideoCapture(0)
    while 1:
        # Get a frame of video
        ret, frame = video_capture.read()
        # window display
        cv2.imshow('Video', frame)
        # Verify 5 photos of face
        if cv2.waitKey(1) & 0xFF == ord('q'):
            for i in range(1, 6):
                cv2.imwrite('recface{}.jpg'.format(i), frame)
            break

    res = []
    for i in range(1, 6):
        with open('recface{}.jpg'.format(i), "rb")as f:
            img = f.read()
            img_data = BytesIO(img)
            im = Image.open(img_data)
            im = im.convert('RGB')
            imgArray = np.array(im)
            predict = predict_image(imgArray)
            if predict:
                res.extend(predict)

    b = set(res)  # {2, 3}
    if len(b) == 1 and len(res) >= 3:
        print("login successfully")
    else:
        print("login fail")


if __name__ == '__main__':
    register_face("maple")
    rec_face()