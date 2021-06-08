from .Database import Database
import datetime


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_waardes_sensor(sensorID):
        sql = "SELECT historiekWaarde, historiekSensor FROM tblHistoriek WHERE historiekSensor = %s order by historiekID DESC LIMIT 1"
        params = [sensorID]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_5waardes_sensor(sensorID):
        sql = "SELECT historiekWaarde, historiekID, historiekTijd FROM tblHistoriek WHERE historiekSensor = %s order by historiekID DESC LIMIT 5"
        params = [sensorID]
        return Database.get_rows(sql, params)

    @staticmethod
    def insert_waarde_sensor(waarde, sensorID):
        sql = "INSERT INTO tblHistoriek(historiekID,historiekTijd,historiekWaarde,historiekSensor) VALUES(NULL,%s,%s,%s)"
        params = [datetime.datetime.now(), waarde, sensorID]
        return Database.execute_sql(sql, params)
