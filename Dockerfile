FROM python:3
RUN pip install board && \
    pip install busio
ADD temperature.py /
CMD [ "python", "./temperature.py" ]
