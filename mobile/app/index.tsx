import { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useRouter } from 'expo-router';
import * as WebBrowser from 'expo-web-browser';

const API_BASE = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

interface Article {
  id: number;
  source_id: string;
  url: string;
  title: string;
  summary: string | null;
  score: number;
  day: string | null;
}

export default function FeedScreen() {
  const router = useRouter();
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchArticles = async () => {
    try {
      const res = await fetch(`${API_BASE}/articles/today`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: Article[] = await res.json();
      setArticles(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load articles');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchArticles();
  };

  const openInBrowser = async (url: string) => {
    await WebBrowser.openBrowserAsync(url);
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6366f1" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{error}</Text>
        <Pressable style={styles.retryButton} onPress={fetchArticles}>
          <Text style={styles.retryText}>Retry</Text>
        </Pressable>
      </View>
    );
  }

  if (articles.length === 0) {
    return (
      <View style={styles.center}>
        <Text style={styles.emptyText}>No articles yet today.</Text>
        <Text style={styles.emptySubText}>
          The pipeline runs at 08:00. Check back later!
        </Text>
      </View>
    );
  }

  return (
    <FlatList
      data={articles}
      keyExtractor={(item) => String(item.id)}
      contentContainerStyle={styles.list}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#6366f1" />
      }
      renderItem={({ item, index }) => (
        <View style={styles.card}>
          <Text style={styles.rank}>#{index + 1}</Text>
          <Pressable onPress={() => router.push(`/article/${item.id}`)}>
            <Text style={styles.title}>{item.title}</Text>
          </Pressable>
          {item.summary ? (
            <Text style={styles.summary} numberOfLines={4}>
              {item.summary}
            </Text>
          ) : null}
          <View style={styles.footer}>
            <Text style={styles.source}>{item.source_id}</Text>
            <Pressable onPress={() => openInBrowser(item.url)}>
              <Text style={styles.readMore}>Read →</Text>
            </Pressable>
          </View>
        </View>
      )}
    />
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1e293b',
    padding: 24,
  },
  list: {
    padding: 12,
    gap: 12,
  },
  card: {
    backgroundColor: '#0f172a',
    borderRadius: 12,
    padding: 16,
    gap: 8,
  },
  rank: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: '700',
  },
  title: {
    color: '#f8fafc',
    fontSize: 16,
    fontWeight: '600',
    lineHeight: 22,
  },
  summary: {
    color: '#94a3b8',
    fontSize: 14,
    lineHeight: 20,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 4,
  },
  source: {
    color: '#475569',
    fontSize: 12,
  },
  readMore: {
    color: '#6366f1',
    fontSize: 14,
    fontWeight: '600',
  },
  errorText: {
    color: '#f87171',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 16,
  },
  retryButton: {
    backgroundColor: '#6366f1',
    paddingHorizontal: 24,
    paddingVertical: 10,
    borderRadius: 8,
  },
  retryText: {
    color: '#fff',
    fontWeight: '600',
  },
  emptyText: {
    color: '#f8fafc',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  emptySubText: {
    color: '#94a3b8',
    fontSize: 14,
    textAlign: 'center',
  },
});
