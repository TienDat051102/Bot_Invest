alter table activity_log 
	Add jobversion text
go

alter table faq 
	Add conversation_id integer
go
alter table faq 
Add timestamp timestamp with time zone 