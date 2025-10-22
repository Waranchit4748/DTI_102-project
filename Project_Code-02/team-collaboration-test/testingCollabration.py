# Project_Code-02

# สำหรับ คัดลอก (clone) repository จาก GitHub 
# git clone ....

# ดู รายชื่อ branch ทั้งหมดในโปรเจกต์
# git branch

# ใช้ สลับ branch หรือ ย้อนกลับไป commit เดิม
# git checkout ...(ชื่อ branch) ควรจะ git checkout main ก่อน

# เก็บการเปลี่ยนแปลงชั่วคราว ที่ยังไม่อยาก commit
# git stash 
# git stash push -u -m " "  เก็บไฟล์ที่แก้ไขไว้ใน stash พร้อมข้อความอธิบาย

# ดูรายการ stash ที่เคยเก็บไว้ทั้งหมด
# git stash list 

# นำโค้ดที่เคย stash ไว้กลับมาใช้งานอีกครั้ง (pop ให้ถูก branch)
# git stash pop 

# เพิ่มไฟล์ที่แก้ไขไว้ใน staging area เพื่อเตรียม commit
# git add . / git add <ไฟล์>

# บันทึกการเปลี่ยนแปลงใน staging area ลงใน repository
# git commit -m ""
# อัปโหลด commit จากเครื่องเรา (local) ไปยัง remote repository
# git push origin .....
print("test game")

