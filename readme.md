## DevOps зима 2026
## Лаб11: 
## CI/CD – непрерывная интеграция, развертывание и доставка

Полная схема стенда CI/CD
![title](./pic/title.png)

CI = Continuous Integration  
Любые коммиты в ветку dev должны автоматически запустить серию интеграционных процессов
- Линтинг
- Юнит-тесты
- Сборка приложения
- Интеграционные тесты

Практика: Создаем Cloud-native приложение для экспериментов
1. Создаем само приложение
2. Создаем юнит тесты для приложения
3. Докеризируем: Создаем докерфайл для сборки контейнера
4. Описываем CI-сценарии для Github Actions производящие lint, unit-test, build-test
5. Куберизируем: Создаем манифесты для запуска приложения и сервисов в кластере
6. Описываем CD-сценарии для Github Actions производящие docker build и push в Docker Hub
7. Устанавливаем ArgoCD и подключаем к GitHub
8. Проверяем весь CI/CD workflow в сборе

### Проверим, что в git есть ключ
![git-ssh-key](./pic/git-ssh-key.png)

git показывает хэш публичного ключа. локально хэш такой же
```
ssh-keygen -l -f ~/.ssh/id_ed25519.pub
```
![key-hash](./pic/key-hash.png)

### Создаём пустой репозиторий

### Приложение
[applicattion.py](./server/application.py) - веб сервер. по умолчанию показывает список файло текущего каталога

[test_application.py](./server/test_application.py) - юнит тесты. Тестируем методы класса TestMe из applicattion.py. Используем библиотеку PyTest

[requirements.txt](./requirements.txt) - файл зависимостей

[dockerfile](./server/dockerfile) - файл для сборки образа

### проверим git
настроил чтоб все изменения уходили по ssh
```
git remote -v
git remote set-url origin git@github.com:alex-zotov/devops-lab11.git
```
![git-remote](./pic/git-remote.png)

```
git status
git add .
git commit -m server
git push
```

запишу временно readme.md и pic в .gitignore
и удалю их временно из индекса (--cached) git
```
git rm --cached readme.md
git rm -r --cached pic
git commit -m ditignore
git push
```

### Переводим разработку в отдельную ветку dev
```
git checkout -b dev
```
эквивалентно 
```
git branch dev      # создать ветку dev
git checkout dev    # переключиться на ветку dev
```

устанавливаем связь локальной ветки и ветки в github
```
git push -u origin dev
```
или эквивалент без сокращений
```
git push --set-upstream origin dev
```
![git-dev](./pic/git-dev.png)

### Защищаем ветку master от прямых изменений
теперь только merge-requests. Все изменения делаем в dev. Для переноса в main идём в гитхаб, и производим merge/pull request > approve 
![protect-main](./pic/protect-main.png)

### Пример
добавляем индексный файл, пушим, открываем pull/merge-request
```
echo "">index.html
git add index.html
git commit -m test
git push
```
![git-push-test](./pic/git-push-test.png)  
![vc-branches-test](./pic/vc-branches-test.png)

идём на githab. открываем pull request
![pull-request-test](./pic/pull-request-test.png)  
![pull-request-test1](./pic/pull-request-test-1.png)  

тимлид делает слияния с main
![pull-request-test2](./pic/pull-request-test-2.png)  
![merge-test](./pic/merge-test.png)


## CI = Continuous Integration. Github Actions

- Создаются в виде скриптов («пайплайн», workflow) из нескольких шагов
- Выполняются на отдельной vm на стороне github («shared runner»)
- Имееют доступ в наш репо
- Могут оставлять артефакты

Разрешаем action
![allow-action](./pic/allow-action.png)

Добавляем CI-пайплайны (сценарии) – Github Actions
![github-dir](./pic/github-dir.png)

### Тестовый сценарий
[devops_course_pipeline.yml](./.github/workflows/devops_course_pipeline.yml) - посмотреть как работает runner на стороне GitHub

отправляем в git
```
git add .github/
git commit -m ci
git push
```
![first-job](./pic/first-job.png)

### Боевой сценарий 
линтер > юнит-тесты > интеграционный тест
[cicd.yml](.github/workflows/cicd.yml)
```
git commit -a -m cicd.yml
git push
```
линтер ругается на docstring
![lint-err](./pic/lint-err.png)

выключим коды сигнатур C0114 C0116 из проверки линтера  
Добавляем в пайплайне [.github/workflows/cicd.yml](.github/workflows/cicd.yml) на стадии линтера ключ -d и перечисляем
коды сигнатур для отключения через запятую
```
pylint -d C0114,C0116 server/application.py
```
или можно прямо в application.py дать указание линтеру
```
# pylint: disable=C0114,C0116
```
![lint-succ](./pic/lint-succ.png)

после правок в takeFive проойдены unit-tests
![unit-test-succ](./pic/unit-test-succ.png)

со стороны тимлида
![merge-pool-request](./pic/merge-pool-request.png)

после слияния веток  
![vc-merge](./pic/vc-merge.png)

сделать бэдж в readme.md  
create status badge - там markdown заготовка  
![create-status-badge](./pic/create-status-badge.png)  

вставил заготовку  
[![LINT-TEST-BUILD-CHECK](https://github.com/alex-zotov/devops-lab11/actions/workflows/cicd.yml/badge.svg)](https://github.com/alex-zotov/devops-lab11/actions/workflows/cicd.yml)

## Создаём для приложения k8s-манифесты
```
mkdir server-k8s-manifests
cd server-k8s-manifests
```

### Continuous Delivery
- Добавляем публикацию докер-образа приложения в хранилище
- Зарегистрироваться в dockerHub и создать паблик-репо для образов
- Этот репо далее укажем как источник образа в k8s манифесте

новый репозиторий в docker hub
![docker-hub](./pic/docker-hub.png)

### Манифест k8s
[app.yml](./server-k8s-manifests/app.yml) и deployment, и service одним файлом. --- отделяют объекты
- release-date: RELEASE-DATE - CI пайплайн будет подставлять новое значение, чтобы ArgoCD «увидел» изменение манифеста
- image: alexmzotov/devops-2026:latest - путь к репозиторию

### Проверяем/запускаем minikube
```
minikube start
```

Там еще могут оставаться контейнеры с прошлых занятий. Удаляем.
```
kubectl get deployments
kubectl get services
kubectl delete services dev-redis dev-web
kubectl delete services prod-redis prod-web
kubectl delete deployments dev-redis dev-web
kubectl delete deployments prod-redis prod-web
```
### Cобираем образ. Выкладываем в dockerHub
Собираем образ приложения в докере. Тэг должен совпадать с именем репозитория в dockerhub
```
docker image build -t alexmzotov/devops-2026 ./server/
```
логинимся в докере
```
docker login
```
кладём образ в docker hub
```
docker push alexmzotov/devops-2026
```
![docker-hub-push](./pic/docker-hub-push.png)


### Применяем манифесты
```
kubectl create namespace devops-psu
kubectl apply -f ./server-k8s-manifests/app.yml
```

в отдельном окне запускаем туннель
```
minikube tunnel
```

проверяем
![kubectl-get-services](./pic/kubectl-get-services.png)
![app-browser-test](./pic/app-browser-test.png)

### Сохраняем манифесты в git
```
git status
git add ./server-k8s-manifests/
git commit -m k8s
git push
```

## CD = Continuous Delivery and/or Deployment
Будем создавать хранилище докер-образов.
CD-служба будет брать из хранилища новые образы и разворачивать их в кластере k8s

### Create Access Token
В профиле DockerHub / Account settings / Personal access tokens / Create access token
![create-access-token](./pic/create-access-token.png)

### Добавляем свои учетные данные как Action Secrets на github
Два секрета – DOCKER_USERNAME и DOCKER_TOKEN  
Settings / Secrets and variables / Actions   
![git-add-secret](./pic/git-add-secret.png)

### Пайплайн для сборки и публикации образа в Docker Hub
[.github/workflows/release.yml](.github/workflows/release.yml)
- **branches: [ master ]** - На этот раз работает в ветке мастер (в неё попадают уже оттестированные изменения).
- **permissions / contents: write** - Разрешаем пайплайну делать коммиты в репозиторий
- **username: \${{ secrets.DOCKER_USERNAME }}** - Логинимся в докер-хаб с использованием секретного токена
- **push: true** - Сохраняем свежий образ на ДокерХабе

Вторая часть (jobs / touch-k8s-manifest:) пайплайна заносит дату сборки в файл манифеста и коммитит в ветку release.  
Это требуется, чтобы на CD стадии мы увидели не просто коммит, а обновление манифеста.

**Note:** Популярна схема, когда приложение лежит в одном репо, а манифесты в отдельном репо.
Пайплайн после сборки образа вносит в репо с манифестами конкретный хэш собранного образа.
Далее на стадии CD будет использоваться не просто latest образ, а образ с конкретным хэшем.

### Пример отработки пайплайна release.yml
Делаем коммит новых файлов в репо, создаем pull-request и выполняем merge в main
![merge-release](./pic/merge-release.png)

видим свежий образ в dockerHub
![dockerhub-image](./pic/dockerhub-image.png)

### На текущий момент стратегия работы с ветками выглядит так
![branch-steps](./pic/branch-steps.png)

## Continuous Deployment: ArgoCD
ArgoCD – инструмент непрерывной доставки в парадигме GitOps

ArgoCD имеет свой CLI и работает декларативно через yml, также имеет WebUI

### Устанавливаем ArgoCD
создаем отдельное пространство имён
```
kubectl create namespace argocd
```

скачиваем и устанавливаем всё из манифеста (в две строчки)
```
kubectl apply -n argocd \
-f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Подождать, пока все модули ArgoCD станут READY 1/1
```
kubectl get deployments -n argocd
```
![kubectl-deployments-argocd](./pic/kubectl-deployments-argocd.png)

Вытаскиваем стартовый админский пароль – он поторебуется для входа в интерфейс (в две строчки)
```
kubectl -n argocd get secret argocd-initial-admin-secret \
--template={{.data.password}} | base64 -d
```

Пробрасываем api-сервис ArgoCD наружу (в две строчки)
```
kubectl patch svc argocd-server -n argocd \
-p '{"spec": {"type": "LoadBalancer"}}'
```
![kubectl-get-services-argocd](./pic/kubectl-get-services-argocd.png)

Используем имя admin и пароль с предыдущего шага
![browse-argocd](./pic/browse-argocd.png)

### Подключаем к ArgoCD наш GitHub репо с использованием приватного ключа
Сгенерируем ключевую пару ssh и(или) возьмем существующую  
У этого ключа должен быть доступ до репо github  
Ключ должен быть без парольной фразы. 
Положить приватный ключ на Argo

Argo / Settings / Repositories
![argocd-add-ssh-key](./pic/argocd-add-ssh-key.png)

![argocd-connect-git](./pic/argocd-connect-git.png)

### Подключаем манифесты приложения для контроля состояния
Application / New App  
New App (1)  
![argocd-create-app-1](./pic/argocd-create-app-1.png)

Выбираем репо, указываем ветку для отслеживания и путь к манифестам  
New App (2)  
![argocd-create-app-2](./pic/argocd-create-app-2.png)

Указываем реквизиты кластера k8s и пространство имен  
New App (3)  
![argocd-create-app-3](./pic/argocd-create-app-3.png)

### Приложение установлено на контроль ArgoCD
![argocd-controled_app](./pic/argocd-controled_app.png)

![argocd-controled-app-detail](./pic/argocd-controled-app-detail.png)

### Проверка
#### Изменяем приложение: добавляем ииндексный файл
- правим содержание индекса
```
echo "Hello! I'm version 2" > ./server/index.html
```
- добавляем индекс в [dockerfile](./server/dockerfile)
```
ADD ./index.html /usr/local/http-server/index.html
```

### Отправляем изменения в ветку dev
```
git status
git commit -a -m index.html
git push
```

### На стороне Github открывает Pull Request
![pull-request](./pic/pull-request.png)

### Проводим «код ревью» и после успешных тестов проводим Merge
![merge](./pic/merge.png)

### На ветке master сработает пайплайн на релиз
новый образ будет отправлен на DockerHub, манифест будет пропатчен  
![publish-image](./pic/publish-image.png)

### ArgoCD подхватит изменения манифеста и синхронизирует состояние в k8s
![argocd-sync](./pic/argocd-sync.png)

![browse-v2](./pic/browse-v2.png)
