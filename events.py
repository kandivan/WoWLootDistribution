class EventSystem:
    def __init__(self):
        self.events = {}

    def register_event(self, event_name, callback):
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(callback)

    def trigger_event(self, event_name, data):
        if event_name in self.events:
            for callback in self.events[event_name]:
                callback(data)
    def on_event_received(self, data):
        # Convert data (object) to DataFrame
        df = self.database.to_df(data)
        
        # Write DataFrame to Postgres
        self.database.write_to_db(data)

        # Write DataFrame to parquet in S3
        self.database.write_to_s3(df, "my_bucket", "my_file.parquet")

        # Write DataFrame to parquet in Azure Blob Storage
        self.database.write_to_azure_blob(df, "my_connection_string", "my_container", "my_blob.parquet")
        