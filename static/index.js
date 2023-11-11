// async function delInput(user_input) {

//     fetch('/delete', {
//         method: "POST",
//         body: JSON.stringify({
//             document: user_input
//         }),
//         headers: {
//             "Content-type": "application/json; charset=UTF-8"
//         }
//     })
//     .then(function( response ){
//         return response.json();
//     })
//     .then(function( result ){
//         console.log(JSON.stringify(result));
//         result_val = result['result'][1]
//             var added_strings = '<div class="">';
//             for (let idx in result_val) {
//                 var temp = '<p>';
//                 temp += result_val[idx];
//                 temp += '<button onclick=delInput("' + result_val[idx] + '") type="button">Delete input</button></p>';
//                 added_strings += temp;
//             };
//             added_strings += '</div>';
//             console.log(added_strings)
//             document.getElementById('wordsAddedToCorpus').innerHTML = added_strings;
//     });
// }

document.addEventListener('DOMContentLoaded', function(){

    document.getElementById('input_corpus_btn').addEventListener('click', sendInputCorpusForTraining);
    // document.getElementById('search_btn').addEventListener('click', searchForWordsHandler);
    // document.getElementById('drop_db').addEventListener('click', dropDBHandler);
    // document.getElementById('q1_btn').addEventListener('click', questionHandler.bind(null, 'q1'));
    // document.getElementById('q2_btn').addEventListener('click', questionHandler.bind(null, 'q2'));
    // document.getElementById('q3_btn').addEventListener('click', questionHandler.bind(null, 'q3'));
    // document.getElementById('q4_btn').addEventListener('click', questionHandler.bind(null, 'q4'));

    async function sendInputCorpusForTraining() {
        var input_corpus = document.getElementById('input_corpus').value;

        fetch('/train', {
            method: "POST",
            body: JSON.stringify({
                input_corpus: input_corpus
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        })
        .then(function( response ){
            return response.json();
        })
        .then(function( result ){
            console.log(JSON.stringify(result));
            // result_val = result['result']
            // var added_strings = '<div class="">';
            // for (let idx in result_val) {
            //     var temp = '<p>';
            //     temp += result_val[idx];
            //     temp += '<button onclick=delInput("' + result_val[idx] + '") type="button">Delete input</button></p>';
            //     added_strings += temp;
            // };
            // added_strings += '</div>';
            // console.log(added_strings)
            // document.getElementById('wordsAddedToCorpus').innerHTML = added_strings;	
        });
    }

    async function questionHandler(question) {
        var question_text = document.getElementById(question).textContent;
        fetch('/answer/' + question_text, {
            method: 'GET',
        })
        .then(function( response ){
            return response.json();
        })
        .then(function( result ){
            console.log(JSON.stringify(result));
            document.getElementById(question + "_ans").innerHTML = "Ans: " + result['result'];
        });
    }
});