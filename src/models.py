from sqlalchemy.orm import declarative_base

import src.user_profile.models

Base = declarative_base()

#Костыль, потом буду думать как исправлять
target_metadata = src.user_profile.models.Base.metadata
