import readAndSave

engoo_id = input("engoo 아이디를 입력하세요: ")
engoo_password = input("engoo 비밀번호를 입력하세요: ")
reserve_time = input("수업 하고 싶은 시간을 적어주세요(예>19-30): ")
class_holiday = input("주말에도 수업하시나요(y/n): ")
teacher_num = [input("수업하고 싶은 선생님 번호를 적어주세요(선생님 번호는 선생님 URL 제일 뒤에 있어요.): ")]# 나중에 list로

more = True
while more:
    another_teacher = input("수업하고 싶은 선생님이 더 있나요? 있으면 번호를, 없다면 nope 을 적어주세요")
    if another_teacher == "nope":
        more = False
    else:
        teacher_num.append(another_teacher)


id_pass = {"engoo":{"id" : engoo_id, "password" : engoo_password},}
reservation_info = {"teacher_num":teacher_num,
                    "reserve_time":reserve_time,
                    "class_holiday": "True" if class_holiday.lower() == "y" else "False",
                    "send_to": ""}

readAndSave.save_json(id_pass,'id_pass.json', 'utf8')
readAndSave.save_json({}, 'Did_I_reserved.json', 'utf8')
readAndSave.save_json(reservation_info, 'reservation_info.json', 'utf8')


