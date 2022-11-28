function logout() {

    fetch("/logout", {'method': 'POST'})
        .then((resp) => { 
            resp.text().then(() => {
                window.location.href = "/"
            })
        });
}

function newgame() {

    fetch("/newgame", {'method': 'POST'})
    .then((resp) => { 
        resp.json().then((game_info) => {
            window.location.href = `/game/${game_info['game_key']}`;
        })
    });
}

function update_screen(game_info) {

    players = ['X', 'O'];

    players.forEach(function(player) {

        game_info[player].forEach(function(move){
            console.log(move);
            div_move = document.getElementById(`pos_${move}`);
            div_move.innerText = player;
        });

    });

    span_message = document.getElementById('ttt_message');
    
    if (game_info['winner'] == '?') {
        // Game is still running
        span_message.innerText = 'Sua vez!';
    }

    if (game_info['winner'] == '*') {
        // Game is still running
        span_message.innerText = 'Jogo Finalizado com Empate!';
    }

    if (game_info['winner'] == 'O') {
        // Game is still running
        span_message.innerText = 'Jogo Finalizado! Você perdeu :(';
    }

    if (game_info['winner'] == 'X') {
        // Game is still running
        span_message.innerText = 'Jogo Finalizado! Você venceu :D';
    }

}

function update_game_info(game_key) {

    fetch(`/game/${game_key}/info`)
    .then((resp) => { 
        if (resp.status == 404) {
            alert('Jogo não encontrado!');
            window.location.href = '/index';
        }
        resp.json().then((game_info) => {
            
            update_screen(game_info);

        });
    });

}

function move(position) {

    var game_key = document.getElementById('key').value;

    fetch(`/game/${game_key}/move`, {
        'method': 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },        
        'body': `position=${position}`
    })
    .then((resp) => { 
        resp.json().then((game_info) => {
            update_screen(game_info);
        })
    });

}

function setup_game() {

    var game_key = document.getElementById('key').value;

    update_game_info(game_key);

}