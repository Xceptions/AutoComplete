document.addEventListener('DOMContentLoaded', function(){

    document.getElementById('input_corpus_btn').addEventListener('click', sendInputCorpusForTraining);
    document.getElementById('complete_btn').addEventListener('click', completeHandler);
    document.getElementById('drop_db').addEventListener('click', dropDBHandler);
    
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

    async function dropDBHandler() {
        fetch('/dropdb')
        .then(function( response ){
            return response.json();
        })
        .then(function( result ){
            console.log(JSON.stringify(result));
        });
    }

    async function completeHandler() {
        var pred_text = document.getElementById('pred_phrase').value;
        console.log(pred_text)
        fetch('/complete/' + pred_text, {
            method: 'GET',
        })
        .then(function( response ){
            return response.json();
        })
        .then(function( result ){
            console.log(JSON.stringify(result));
            document.getElementById("prediction").innerHTML = result['result'];
        });
    }
});