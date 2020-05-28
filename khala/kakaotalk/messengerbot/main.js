const scriptName="uwo.js";

function msg2response(msg, sender){
    Log.d("[msg2response] msg "+msg);
    var newline="_=_=_";
    //var host = "6abc8164.ngrok.io";
    var host="henrique.way2gosu.com";
    var endpoint = "http://"+host+"/khala/kakaotalk/query";
    var url = endpoint+"?sender_name="+encodeURI(sender)+"&text="+msg+"&newline="+newline;
    var html = Utils.getWebText(url);

    Log.d("html "+html);
    var content = html.split("<body>")[1].split("</body>")[0].trim();
    Log.d("content: "+content);

    if(!content){ return; }

    var text_out = content.split(newline).join("\n");
    Log.d("[msg2response] text_out: "+text_out);
    return text_out;
}

function word2chunks(word, limit){
    Log.d("[word2chunks] word: "+word);
    var i;
    var chunks = [];
    for(i=0; i*limit<msg.length; i++){
        var start = i*limit;
        var end = Math.min((i+1)*limit, msg.length);
        chunks.push(word.substring(start,end));
    }
    Log.d("[word2chunks] chunks: "+chunks);
    return chunks;
}
function extend(l1, l2){
    var j;
    for(j=0; j<l2.length; j++){
        l1.push(l2[j]);
    }
    return l1;
}

function msg2chunks(msg, limit){
    Log.d("[msg2chunks] msg: "+msg);

    var chunks = [];
    lines = msg.split(/\r?\n/);

    var i;
    var current = "";
    for(i=0; i<lines.length; i++){
        var line = lines[i];

        if((current + "\n"+line).length > limit){
            if(current){ chunks.push(current); }

            if(line.length>limit){
                chunks = extend(chunks, word2chunks(line, limit));
                current = "";
            }
            else {
                current = line;
            }
        }
        else{
            current += "\n" + line;
        }

        current = current.trim();
    }

    if(current){
        chunks.push(current);
    }

    Log.d("[msg2chunks] chunks: "+chunks);
    return chunks;

}

function response(room, msg, sender, isGroupChat, replier, ImageDB, packageName, threadId){
    var response = msg2response(msg, sender);
    if (!response){ return; }

    var chunks = msg2chunks(response, 200);
    var i;
    for(i=0; i<chunks.length; i++){
        replier.reply(chunks[i]);
    }
}

function onStartCompile(){}
//아래 4개의 메소드는 액티비티 화면을 수정할때 사용됩니다.
function onCreate(savedInstanceState,activity) {
    var layout=new android.widget.LinearLayout(activity);
    layout.setOrientation(android.widget.LinearLayout.HORIZONTAL);
    var txt=new android.widget.TextView(activity);
    txt.setText("액티비티 사용 예시입니다.");
    layout.addView(txt);
    activity.setContentView(layout);
}
function onResume(activity) {}
function onPause(activity) {}
function onStop(activity) {}