FROM python:3.8
COPY . .
RUN pip install selenium
CMD ["python", "./main.py"]