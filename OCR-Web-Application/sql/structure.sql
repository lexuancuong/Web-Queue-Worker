drop table if exists UploadedImage;
drop table if exists ProcessedImage;
create table UploadedImage(
  id varchar(100),
  url_image varchar(255),
  status varchar(10),
  PRIMARY KEY (id)
) ENGINE=INNODB; 

create table ProcessedImage(
  id varchar(100),
  url_image varchar(255),
  text_result varchar(255),
  PRIMARY KEY(id, url_image),
  FOREIGN KEY (id) references UploadedImage(id)
) ENGINE=INNODB;