workspace {
  model {
    user = person "Пользователь" "Пользователь приложения для знакомств"

    s3 = softwareSystem "AWS S3" "Облачное хранилище для фотографий пользователей" {
      tags "thirdparty"
    }

    Kindle = softwareSystem "Приложение для знакомств Kindle" {
      auth = container "Auth API" "Регистрация, вход, токены" "FastAPI + SQLAlchemy" {
        tags "backend"
      }

      user_profile = container "User Profile Service" "Управляет личными данными пользователя" "FastAPI" {
        tags "backend"
      }

      image_service = container "Image Service" "Прокси-сервис для работы с изображениями" "FastAPI + boto3" {
        tags "backend"
      }

      profile_deck = container "Profile Deck Service" "Лента просмотра профилей" "FastAPI" {
        tags "backend"
      }

      swipe = container "Swipe Service" "Обработка свайпов и мэтчей" "FastAPI" {
        tags "backend"
      }

      notifications = container "Notifications" "Микросервис уведомлений о лайках/метчах" "FastAPI" {
        tags "backend"
      }

      kafka = container "Kafka" "Система брокера сообщений для обработки событий уведомлений" "Apache Kafka" {
        tags "broker"
      }

      database = container "База данных" "Основное хранилище данных" "PostgreSQL + PostGIS" {
        tags "database"
      }

      cache = container "Кеш" "Redis для временных данных" "Redis" {
        tags "cache"
      }

      web_server = container "Nginx" "Reverse proxy и отдача статики" "Nginx" {
        tags "web"
      }
    }

    # Взаимодействия

    user -> web_server "HTTP-запросы к веб-приложению" "HTTP/JSON"

    web_server -> auth "Проксирует запросы на регистрацию, вход, выход" "HTTP/JSON"
    web_server -> user_profile "Проксирует запросы на личный профиль" "HTTP/JSON"
    web_server -> profile_deck "Проксирует запросы на просмотр ленты" "HTTP/JSON"
    web_server -> swipe "Проксирует запросы на свайпы и мэтчи" "HTTP/JSON"

    auth -> database "Читает и сохраняет данные пользователя" "SQL/ORM"
    auth -> cache "Сохраняет и извлекает токены/сессии" "Redis protocol"

    user_profile -> image_service "Запросы на загрузку, удаление, получение изображений" "HTTP/JSON"
    image_service -> s3 "Загрузка и удаление изображений" "HTTPS (AWS SDK)"
    image_service -> database "Сохраняет метаданные изображений (URL, ключи и т.п.)" "SQL/ORM"

    user_profile -> database "Чтение и обновление данных профиля" "SQL/ORM"
    user_profile -> cache "Кэширует информацию профиля" "Redis protocol"

    profile_deck -> database "Чтение анкет пользователей" "SQL/ORM"
    profile_deck -> cache "Кэш популярных профилей" "Redis protocol"

    swipe -> database "Сохраняет лайки и мэтчи" "SQL/ORM"
    swipe -> user_profile "Запрашивает данные о пользователях при мэтче" "HTTP/JSON"
    swipe -> kafka "Публикует события мэтча" "Kafka topic"

    notifications -> kafka "Подписывается на события мэтча" "Kafka topic"
  }

  views {
    systemContext Kindle "SystemContext" {
      include *
      //autolayout tb
    }

    container Kindle "ContainerView" {
      include *
      //autolayout lr
    }

    styles {
      element "database" {
        shape cylinder
        background #3366cc
        color #ffffff
      }

      element "cache" {
        shape pipe
        background #cc0000
        color #ffffff
      }

      element "thirdparty" {
        background #eeeeee
        color #000000
        shape folder
      }

      element "web" {
        shape webbrowser
        background #1e90ff
        color #ffffff
      }

      element "backend" {
        shape roundedbox
        background #4caf50
        color #ffffff
      }

      element "broker" {
        shape pipe
        background #ff9900
        color #000000
      }
    }

    theme default
  }
}
