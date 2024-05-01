var counter = 0;
var timer;

document.addEventListener('DOMContentLoaded', () => {

    if (document.querySelector('#counter')) {
        count();
    } else {
        clearInterval(timer);
        counter = 0;
    }

    if (document.querySelector('.meeting-buttons')) {
        const cancelBut = document.querySelector('#cancel-meeting');
        const restartBut = document.querySelector('#restart-meeting');
        const finishBut = document.querySelector('#finish-meeting');

        cancelBut.addEventListener('click', (event) => {
            event.preventDefault();
            if (confirm('Deseja cancelar a reunião?')) {
                clearInterval(timer);
                counter = 0;
                window.location.href = '/meeting';
            }
        });
        restartBut.addEventListener('click', (event) => {
            event.preventDefault();
            if (confirm('Deseja reiniciar a reunião?')) {
                clearInterval(timer);
                counter = 0;
                count();
            }
        });
        finishBut.addEventListener('click', (event) => {
            event.preventDefault();
            if (confirm('Tem certeza que deseja finalizar a reunião?\nNão esqueça de enviar a ata da reunião')) {
                const formulario = document.getElementById('forms-file');

                const formData = new FormData(formulario);
                formData.append('duration', parseInt(counter));
                const formMembers = document.getElementById('form-members');

                const membrosSelecionados = [];

                formMembers.querySelectorAll('input[type="radio"]').forEach((radioInput) => {
                    if (radioInput.checked) {
                        membrosSelecionados.push(radioInput.value);
                    }
                });
                if (membrosSelecionados.length === 0) {
                    alert('Selecione pelo menos um membro para a reunião');
                    return;
                }
                formData.append('members', membrosSelecionados);

                fetch(`/meeting/${finishBut.dataset.id}/${finishBut.dataset.type}`, {
                    method: 'POST',
                    body: formData
                    })
                    .then(response => response.json())
                    .then(result => {
                        clearInterval(timer);
                        counter = 0;
                        window.location.href = '/meeting';
                    })
                    .catch(error => {
                        console.log('Error:', error);
                    });
            }
        });
    }

    if (document.querySelector('#meeting-select')) {
        document.querySelector('#meeting-select').addEventListener('change', (event) => {
            event.preventDefault();
            const elementSelect = document.querySelector('#meeting-select');
            if (elementSelect.value !== '00') {
                document.querySelector('#start-meeting').disabled = false;
            } else {
                document.querySelector('#start-meeting').disabled = true;
            }
        });
    }

    if (document.querySelector('#start-meeting')) {
        document.querySelector('#start-meeting').addEventListener('click', (event) => {
            event.preventDefault();
            startMeeting();
            count();
        });
    }

    window.addEventListener('click', (event) => {
        const element = event.target;
        if (element.classList.contains('day-desactive')) {
            event.preventDefault();
            showDayInfo(element);
        }
        if (element.parentElement) {
            if (element.parentElement.classList.contains('day-desactive')) {
                event.preventDefault();
                showDayInfo(element.parentElement);
            }
            if (element.parentElement.parentElement) {
                if (element.parentElement.parentElement.classList.contains('day-desactive')) {
                    event.preventDefault();
                    showDayInfo(element.parentElement.parentElement);
                }
            }
        }
    });
    if (document.querySelector('#form-compose-bio')) {
        document.querySelector('#form-compose-bio').addEventListener('submit', (event) => {
            event.preventDefault();
            changeBio();
        });
    }
    if (document.querySelector("#button-bio-edit")) {
        document.querySelector("#button-bio-edit").addEventListener('click', (event) => {
            event.preventDefault();
            document.querySelector('#bio-show').style.display = 'none';
            document.querySelector('#bio-form').style.display = 'block';
        });
    }

    if (document.querySelector('#form-compose-des')) {
        document.querySelector('#form-compose-des').addEventListener('submit', (event) => {
            event.preventDefault();
            changeDes();
        });
    }
    if (document.querySelector("#button-des-edit")) {
        document.querySelector("#button-des-edit").addEventListener('click', (event) => {
            event.preventDefault();
            document.querySelector('#des-show').style.display = 'none';
            document.querySelector('#des-form').style.display = 'block';
        });
    }

});

function startMeeting() {
    var selectElement = document.getElementById('meeting-select');
    var selectedOption = selectElement.options[selectElement.selectedIndex];
    var reuniaoId = selectedOption.value;
    var typeInfo = selectedOption.dataset.type;

    if (reuniaoId !== "00" && typeInfo) {
        window.location.href = `/meeting/${reuniaoId}/${typeInfo}`;
    } else {
        alert('Selecione uma opção válida');
    }
}

function count() {
    timer = setInterval(() => {
        counter++;
        let hours = Math.floor((counter / 60) / 60);
        let minutes = Math.floor(counter / 60 - (hours * 60));
        let seconds = Math.floor(counter % 60);

        if (seconds < 10) {
            seconds = `0${seconds}`;
        }
        if (minutes < 10) {
            minutes = `0${minutes}`;
        }
        if (hours < 10) {
            hours = `0${hours}`;
        }
        document.querySelector('#counter').innerHTML = `${hours}:${minutes}:${seconds}`;
    }, 1000);
}


function showDayInfo(element) {
    if (document.querySelector('.day-active')) {
        const activeDay = document.querySelector('.day-active')
        const dayActive = activeDay.dataset.day;
        const weekdayActive = activeDay.dataset.weekday;
        
        activeDay.className = 'day-desactive';
        document.getElementById(`${dayActive}-${weekdayActive}`).style.display = 'none';

    }
    element.className = 'day-active';
    const day = element.dataset.day;
    const weekday = element.dataset.weekday;
    document.getElementById(`${day}-${weekday}`).style.display = 'block';
}

function changeDes() {
    const content = document.querySelector('#content-des-compose');
    const text = content.value;
    const type = content.dataset.type;
    const id = content.dataset.id;
    let error_message = document.querySelector("#error");
    if (!text.trim()) {
        console.log('Error: No text to post');
        error_message.style.display = 'block';
        error_message.innerHTML = 'No text to post';
        setTimeout(() => {
            error_message.style.display = 'none';
        }, 3000);
        return;
    } else if (text.length > 300) {
        console.log('Error: Text too long');
        error_message.style.display = 'block';
        error_message.innerHTML = 'Text too long';
        setTimeout(() => {
            error_message.style.display = 'none';
        }, 3000);
        return;
    } else {
        fetch(`/display/${type}/${id}`, {
            method: 'POST',
            body: JSON.stringify({
                text: text,
                type: type
            })
          })
          .then(response => response.json())
          .then(result => {
            console.log(result);
            document.querySelector('#des-form').style.display = 'none';

            document.querySelector('#content-des').innerHTML = text;
            document.querySelector('#des-show').style.display = 'block';

          })
          .catch(error => {
              console.log('Error:', error);
          });
    }
}

function changeBio() {
    const text = document.querySelector('#content-bio-compose').value;
    let error_message = document.querySelector("#error");
    if (!text.trim()) {
        console.log('Error: No text to post');
        error_message.style.display = 'block';
        error_message.innerHTML = 'No text to post';
        setTimeout(() => {
            error_message.style.display = 'none';
        }, 3000);
        return;
    } else if (text.length > 300) {
        console.log('Error: Text too long');
        error_message.style.display = 'block';
        error_message.innerHTML = 'Text too long';
        setTimeout(() => {
            error_message.style.display = 'none';
        }, 3000);
        return;
    } else {
        fetch('/bio', {
            method: 'POST',
            body: JSON.stringify({
                text: text
            })
          })
          .then(response => response.json())
          .then(result => {
            console.log(result);
            document.querySelector('#bio-form').style.display = 'none';

            document.querySelector('#content-bio').innerHTML = text;
            document.querySelector('#bio-show').style.display = 'block';

          })
          .catch(error => {
              console.log('Error:', error);
          });
    }
}