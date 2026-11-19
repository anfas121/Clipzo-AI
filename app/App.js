import React, { useState } from 'react';
import { SafeAreaView, ScrollView, Text, TouchableOpacity, View, TextInput, Alert, ActivityIndicator, Linking, StyleSheet } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { StatusBar } from 'expo-status-bar';

export default function App() {
  const [server, setServer] = useState('http://192.168.1.10:8000');
  const [video, setVideo] = useState(null);
  const [clips, setClips] = useState([]);
  const [videoId, setVideoId] = useState(null);
  const [transcribed, setTranscribed] = useState(false);
  const [busy, setBusy] = useState(false);

  async function pick() {
    const result = await DocumentPicker.getDocumentAsync({ type: 'video/*', copyToCacheDirectory: true });
    if (!result.canceled) { setVideo(result.assets[0]); setClips([]); setVideoId(null); setTranscribed(false); }
  }
  async function process() {
    if (!video) return Alert.alert('Choose a video first');
    setBusy(true);
    try {
      const base = server.trim().replace(/\/$/, '');
      const form = new FormData();
      form.append('file', { uri: video.uri, name: video.name || 'video.mp4', type: video.mimeType || 'video/mp4' });
      const uploaded = await fetch(base + '/videos', { method: 'POST', body: form });
      if (!uploaded.ok) throw new Error(await uploaded.text());
      const info = await uploaded.json();
      const response = await fetch(base + '/videos/' + info.id + '/suggestions?clip_seconds=30');
      if (!response.ok) throw new Error(await response.text());
      const data = await response.json();
      setVideoId(info.id);
      setTranscribed(false);
      setClips(data.clips.map(clip => ({ ...clip, videoId: info.id })));
    } catch (error) {
      Alert.alert('Processing failed', String(error.message || error));
    } finally { setBusy(false); }
  }
  async function transcribeVideo() {
    if (!videoId) return Alert.alert('Process a video first');
    setBusy(true);
    try {
      const base = server.trim().replace(/\\/$/, '');
      const result = await fetch(base + '/videos/' + videoId + '/transcribe', { method: 'POST' });
      if (!result.ok) throw new Error(await result.text());
      const response = await fetch(base + '/videos/' + videoId + '/suggestions?clip_seconds=30');
      if (!response.ok) throw new Error(await response.text());
      const data = await response.json();
      setClips(data.clips.map(clip => ({ ...clip, videoId })));
      setTranscribed(true);
    } catch (error) { Alert.alert('Transcription unavailable', String(error.message || error)); }
    finally { setBusy(false); }
  }
  function clipUrl(clip, captions = false) {
    return server.trim().replace(/\\/$/, '') + '/videos/' + clip.videoId +
      '/export?start=' + clip.start + '&end=' + clip.end + (captions ? '&burn_captions=true' : '');
  }
  return (
    <SafeAreaView style={styles.screen}>
      <StatusBar style="light" />
      <ScrollView>
        <Text style={styles.title}>Clipzo AI ✂️</Text>
        <Text style={styles.muted}>Turn long videos into vertical shorts.</Text>
        <Text style={styles.text}>Backend URL</Text>
        <TextInput style={styles.input} value={server} onChangeText={setServer} autoCapitalize="none" keyboardType="url" />
        <TouchableOpacity style={styles.button} onPress={pick}><Text style={styles.buttonText}>Choose video</Text></TouchableOpacity>
        {video && <Text style={styles.muted}>{video.name}</Text>}
        <TouchableOpacity style={styles.button} onPress={process} disabled={busy}>
          <Text style={styles.buttonText}>{busy ? 'Processing…' : 'Find clip suggestions'}</Text>
        </TouchableOpacity>
        {videoId && <TouchableOpacity style={styles.button} onPress={transcribeVideo} disabled={busy}>
          <Text style={styles.buttonText}>Transcribe & improve suggestions (optional)</Text>
        </TouchableOpacity>}
        {busy && <ActivityIndicator color="#a78bfa" />}
        {clips.map((clip, index) => (
          <View key={index} style={styles.card}>
            <Text style={styles.text}>Clip {index + 1}: {clip.start}s – {clip.end}s (audio score: {clip.score ?? 'N/A'} dB)</Text>
            <TouchableOpacity style={styles.button} onPress={() => Linking.openURL(clipUrl(clip))}>
              <Text style={styles.buttonText}>Preview / download MP4</Text>
            </TouchableOpacity>
            {transcribed && <TouchableOpacity style={styles.button} onPress={() => Linking.openURL(clipUrl(clip, true))}>
              <Text style={styles.buttonText}>Export with burned subtitles</Text>
            </TouchableOpacity>}
            {transcribed && <TouchableOpacity style={styles.button} onPress={() => Linking.openURL(
              server.trim().replace(/\\/$/, '') + '/videos/' + clip.videoId + '/captions?start=' + clip.start + '&end=' + clip.end
            )}><Text style={styles.buttonText}>Open SRT captions</Text></TouchableOpacity>}
          </View>
        ))}
        <Text style={styles.muted}>Prototype: audio and optional speech-density ranking, not semantic AI. Download options depend on your browser. Only upload videos you are authorized to edit.</Text>
      </ScrollView>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#0b1020', padding: 22 },
  title: { fontSize: 34, color: 'white', fontWeight: '800', marginTop: 32 },
  muted: { color: '#a8b3ca', fontSize: 15, marginVertical: 14 },
  button: { backgroundColor: '#7c3aed', borderRadius: 14, padding: 17, marginVertical: 9 },
  buttonText: { color: 'white', fontWeight: '700', textAlign: 'center' },
  card: { backgroundColor: '#192139', padding: 18, borderRadius: 15, marginVertical: 8 },
  text: { color: 'white' },
  input: { backgroundColor: '#192139', color: 'white', padding: 13, borderRadius: 10, marginVertical: 8 }
});
