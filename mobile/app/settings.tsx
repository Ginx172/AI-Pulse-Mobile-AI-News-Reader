import { ScrollView, StyleSheet, Text, View } from 'react-native';

export default function SettingsScreen() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Settings</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <Text style={styles.body}>
          AI Pulse aggregates the Top 100 AI information sources and delivers
          the best 25 stories to your phone every day.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Pipeline</Text>
        <Text style={styles.body}>
          Articles are refreshed daily at 08:00 (Europe/Bucharest). Pull-to-refresh
          on the Feed screen to see the latest results.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Coming soon</Text>
        <Text style={styles.body}>
          • Push notifications{'\n'}
          • Bookmarks{'\n'}
          • Personalization{'\n'}
          • Dark / light theme toggle
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1e293b',
  },
  content: {
    padding: 20,
    gap: 20,
  },
  heading: {
    color: '#f8fafc',
    fontSize: 26,
    fontWeight: '700',
  },
  section: {
    backgroundColor: '#0f172a',
    borderRadius: 12,
    padding: 16,
    gap: 8,
  },
  sectionTitle: {
    color: '#6366f1',
    fontSize: 14,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  body: {
    color: '#94a3b8',
    fontSize: 15,
    lineHeight: 22,
  },
});
