import datetime


MOCK_USERS = [
    {
        'email': 'test@example.com',
        'salt': 'y0VixYUXLQW8O/JNVNx0MLaoaFs=',
        'hashed': 'b2a249015177081552a652d3f3611275cbbc0eac268fb8592adbb6af977811fec0873a95cdc8f6a48b8e9f9c71194993c2f9feb2b7e3fdc67cb334d1c270d894',
    }
]

MOCK_TABLES = [
    {'_id': '1', 'number': '1', 'owner': 'test@example.com', 'url': 'mockurl'},
]

MOCK_REQUESTS = [
    {'_id': '1', 'table_number': '1', 'table_id': '1', 'time': datetime.datetime.now()},
]

class MockDBHelper:

    def get_user(self, email):
        user = [x for x in MOCK_USERS if x.get('email') == email]
        if user:
            return user[0]
        return None

    def add_user(self, email, salt, hashed):
        MOCK_USERS.append({
            'email': email,
            'salt': salt,
            'hashed': hashed,
        })

    def add_table(self, number, owner):
        MOCK_TABLES.append({'_id': number, 'number': number, 'owner': owner})
        return number

    def update_table(self, _id, url):
        for table in MOCK_TABLES:
            if table.get('_id') == _id:
                table['url'] = url
                break

    def get_table(self, table_id):
        for table in MOCK_TABLES:
            if table.get('_id') == table_id:
                return table
        return None

    def get_tables(self, owner_id):
        return MOCK_TABLES

    def delete_table(self, tableid):
        for i, table in enumerate(MOCK_TABLES):
            if table.get('_id') == tableid:
                del MOCK_TABLES[i]
                break

    def add_request(self, tid, time):
        table = self.get_table(tid)
        if table:
            MOCK_REQUESTS.append(
                {'_id': tid, 'table_number': table['number'], 'time': time})

    def get_requests(self, owner_id):
        return MOCK_REQUESTS

    def delete_request(self, request_id):
        for i, request in enumerate(MOCK_REQUESTS):
            if request.get('_id') == request_id:
                del MOCK_REQUESTS[i]
                break
