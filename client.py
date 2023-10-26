import time
from fastapi import FastAPI, UploadFile
import os
import httpx

app = FastAPI()

# URL адрес второго сервера
second_server_url = "http://localhost:8001/receive_images/"

# Путь к папкам с изображениями на сервере отправителя
folder1 = "/Users/aroslavsapoval/myProjects/images_grpc_1980/left"
folder2 = "/Users/aroslavsapoval/myProjects/images_grpc_1980/right"
results = []

async def run_send_images():

    for _ in range(10):
        response = await send_images()  # Вызываем send_images 10 раз
        results.append(response["total_time"])
        # async with httpx.AsyncClient() as client:
        #     # Отправляем POST-запрос на ваш эндпоинт
        #     response = await client.post("http://0.0.0.0:8000/send-images/")

    # Печатаем результаты
    for i, total_time in enumerate(results):
        print(f"Результат {i + 1}: {total_time} секунд")




@app.post("/send-images/")
async def send_images():
    try:
        # Получение списка файлов из папок
        files1 = sorted(os.listdir(folder1))
        print(files1)
        files2 = sorted(os.listdir(folder2))
        print(files2)

        # Проверка, что количество файлов в папках совпадает
        if len(files1) != len(files2):
            return {"message": "Mismatch in the number of files in folders."}

        total_time = 0

        async with httpx.AsyncClient() as client:
            # Организация цикла для отправки каждой пары изображений
            for i in range(len(files1)):
                file1_path = os.path.join(folder1, files1[i])
                file2_path = os.path.join(folder2, files2[i])
                print("file1_path - ", file1_path)
                print("file2_path - ", file2_path)

            # for filename1, filename2 in zip(files1, files2):
            #     file1_path = os.path.join(folder1, filename1)
            #     print("file1_path - ", file1_path)
            #     file2_path = os.path.join(folder2, filename2)
            #     print("file2_path - ", file2_path)

                # Отправляем пару изображений на второй сервер
                with open(file1_path, "rb") as file1, open(file2_path, "rb") as file2:
                    file1_bytes = file1.read()  # Прочитать содержимое файла 1 в виде байтов
                    file2_bytes = file2.read()
                    data = {"image_name": files1[i], "image_name_2": files2[i]}  # Используем имя первого изображения для уникальности
                    start_time = time.time()  # Засекаем время передачи
                    response = await client.post(second_server_url, files={"file1": file1_bytes, "file2": file2_bytes}, data=data)
                    end_time = time.time()  # Засекаем время завершения передачи
                    transfer_time = end_time - start_time
                    total_time += transfer_time

                    response_data = response.json()

                    if response.status_code == 200:
                        # print(f"Images {filename1} and {filename2} sent successfully.")
                        print(f"время передачи этой пары изображений: {transfer_time} секунд.")
                        print("Ответ сервера:", response.text)
                    else:
                        print(f"Error sending images {files1[i]} and {files2[i]}: {response_data['message']}")
            print(f"Общее время передачи изображений: {total_time} секунд.")
            # results.append(total_time)
            print(f"Среднее время передачи изображения - {total_time/len(files1)} секунд.")
        return {"message": "Images sent successfully.", "total_time": total_time}
    except Exception as e:
        return {"message": f"Error sending images: {str(e)}"}







if __name__ == "__main__":
    import uvicorn
    import asyncio

    asyncio.run(run_send_images())
    uvicorn.run(app, host="0.0.0.0", port=8000)
