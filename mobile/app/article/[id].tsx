import { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useLocalSearchParams, useNavigation } from 'expo-router';
import * as WebBrowser from 'expo-web-browser';

const API_BASE = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

interface Article {
  id: number;
  source_id: string;
  url: string;
  title: string;
  author: string | null;
  published_at: string | null;
  summary: string | null;
  score: number;
}

export default function ArticleDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const navigation = useNavigation();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/articles/${id}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data: Article = await res.json();
        setArticle(data);
        navigation.setOptions({ title: data.title.slice(0, 40) + '…' });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load article');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6366f1" />
      </View>
    );
  }

  if (error || !article) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{error ?? 'Article not found'}</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.source}>{article.source_id}</Text>
      <Text style={styles.title}>{article.title}</Text>
      {article.author ? <Text style={styles.meta}>By {article.author}</Text> : null}
      {article.published_at ? (
        <Text style={styles.meta}>
          {new Date(article.published_at).toLocaleDateString()}
        </Text>
      ) : null}
      {article.summary ? (
        <Text style={styles.summary}>{article.summary}</Text>
      ) : null}
      <Pressable
        style={styles.button}
        onPress={() => WebBrowser.openBrowserAsync(article.url)}
      >
        <Text style={styles.buttonText}>Read full article →</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1e293b',
  },
  container: {
    flex: 1,
    backgroundColor: '#1e293b',
  },
  content: {
    padding: 20,
    gap: 12,
  },
  source: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  title: {
    color: '#f8fafc',
    fontSize: 22,
    fontWeight: '700',
    lineHeight: 30,
  },
  meta: {
    color: '#475569',
    fontSize: 13,
  },
  summary: {
    color: '#cbd5e1',
    fontSize: 16,
    lineHeight: 24,
    marginTop: 8,
  },
  button: {
    backgroundColor: '#6366f1',
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 16,
  },
  buttonText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 16,
  },
  errorText: {
    color: '#f87171',
    fontSize: 16,
  },
});
