import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:html';
import 'package:audioplayers/audioplayers.dart';

void main() {
  runApp(YuiApp());
}

class YuiApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Project Yui',
      home: ChatPage(),
    );
  }
}

class ChatPage extends StatefulWidget {
  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> _messages = [];
  final player = AudioPlayer();

  // 🔥 네 IP로 바꿔야 함
  final String serverUrl = "http://192.168.0.15:5001/chat";

  String lastSpeech = "";
  bool isListening = false;

  // 🎤 음성 인식
  void startListening() {
    if (isListening) return;

    isListening = true;

    var recognition = SpeechRecognition();
    recognition.lang = 'ko-KR';
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onResult.listen((event) {
      final results = event.results;

      if (results == null || results.length == 0) {
        isListening = false;
        return;
      }

      final transcript = results[0][0].transcript ?? "";

      recognition.stop();
      isListening = false;

      if (transcript.isEmpty) return;
      if (transcript == lastSpeech) return;
      lastSpeech = transcript;

      _controller.text = transcript;
      sendMessage(transcript);
    });

    recognition.onEnd.listen((event) {
      isListening = false;
    });

    recognition.start();
  }

  // 💬 메시지 전송
  Future<void> sendMessage(String text) async {
    setState(() {
      _messages.add({"role": "user", "content": text});
    });

    try {
      final response = await http.post(
        Uri.parse(serverUrl),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"message": text}),
      );

      final data = jsonDecode(response.body);

      setState(() {
        _messages.add({"role": "yui", "content": data["reply"]});
      });

      // 🔊 음성 재생
      await player.play(
        UrlSource("http://192.168.0.15:5001/voice.mp3"),
      );

    } catch (e) {
      setState(() {
        _messages.add({"role": "yui", "content": "서버 연결 실패"});
      });
    }
  }

  // 💬 말풍선
  Widget buildMessage(Map<String, String> msg) {
    bool isUser = msg["role"] == "user";

    return Container(
      margin: EdgeInsets.symmetric(vertical: 4, horizontal: 8),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          Container(
            padding: EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isUser ? Colors.blue : Colors.grey[300],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              msg["content"]!,
              style: TextStyle(
                color: isUser ? Colors.white : Colors.black,
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Project Yui")),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              children: _messages.map((msg) => buildMessage(msg)).toList(),
            ),
          ),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    maxLines: null,
                    textInputAction: TextInputAction.send,
                    decoration: InputDecoration(
                      hintText: "유이에게 말해보세요...",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                    onSubmitted: (value) {
                      if (value.isNotEmpty) {
                        sendMessage(value);
                        _controller.clear();
                      }
                    },
                  ),
                ),

                // 🎤 마이크
                IconButton(
                  icon: Icon(Icons.mic),
                  onPressed: () {
                    startListening();
                  },
                ),

                // 📤 전송
                IconButton(
                  icon: Icon(Icons.send),
                  onPressed: () {
                    if (_controller.text.isNotEmpty) {
                      sendMessage(_controller.text);
                      _controller.clear();
                    }
                  },
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}