import 'dart:async';

import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/trip.dart';
import '../services/api_client.dart';

class TripDetailScreen extends StatefulWidget {
  const TripDetailScreen({super.key, required this.initialTrip});

  final Trip initialTrip;

  @override
  State<TripDetailScreen> createState() => _TripDetailScreenState();
}

class _TripDetailScreenState extends State<TripDetailScreen> {
  final _api = ApiClient();
  late Trip _trip = widget.initialTrip;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _startPolling();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _startPolling() {
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 2), (_) async {
      if (_trip.status == 'ready' || _trip.status == 'failed') {
        _timer?.cancel();
        return;
      }
      final updated = await _api.getTrip(_trip.id);
      if (mounted) setState(() => _trip = updated);
    });
  }

  Future<void> _regenerate() async {
    final updated = await _api.regenerateTrip(_trip.id);
    if (!mounted) return;
    setState(() => _trip = updated);
    _startPolling();
  }

  @override
  Widget build(BuildContext context) {
    final plan = _trip.plan;
    return Scaffold(
      appBar: AppBar(
        title: Text(_trip.destination),
        actions: [
          IconButton(
            tooltip: '重新生成',
            onPressed: _trip.status == 'generating' ? null : _regenerate,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: SafeArea(
        child: plan == null ? _buildStateView() : _buildPlan(plan),
      ),
    );
  }

  Widget _buildStateView() {
    if (_trip.status == 'failed') {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(_trip.error ?? '生成失败', textAlign: TextAlign.center),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: _regenerate,
                icon: const Icon(Icons.refresh),
                label: const Text('重新生成'),
              ),
            ],
          ),
        ),
      );
    }
    return const Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('正在结合天气、地图和偏好生成行程...'),
        ],
      ),
    );
  }

  Widget _buildPlan(Map<String, dynamic> plan) {
    final days = _asMapList(plan['days']);
    final advice = _asStringList(plan['weather_advice']);
    final budget = _asMap(plan['budget_summary']);
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(plan['summary']?.toString() ?? '旅行计划', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        if (advice.isNotEmpty) _AdviceBox(advice: advice),
        if (budget.isNotEmpty) ...[
          const SizedBox(height: 12),
          _BudgetBox(budget: budget),
        ],
        const SizedBox(height: 16),
        Text('每日计划', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        for (final day in days) _DaySummaryCard(day: day),
      ],
    );
  }
}

class DayPlanScreen extends StatelessWidget {
  const DayPlanScreen({super.key, required this.day});

  final Map<String, dynamic> day;

  @override
  Widget build(BuildContext context) {
    final dayNumber = day['day'] ?? '-';
    return Scaffold(
      appBar: AppBar(title: Text('Day $dayNumber')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _DayWeatherCard(day: day),
            const SizedBox(height: 12),
            _DaySection(day: day),
          ],
        ),
      ),
    );
  }
}

class _DayWeatherCard extends StatelessWidget {
  const _DayWeatherCard({required this.day});

  final Map<String, dynamic> day;

  @override
  Widget build(BuildContext context) {
    final detail = _asMap(day['weather_detail']);
    final weather = day['weather']?.toString();
    if (detail.isEmpty && (weather == null || weather.isEmpty)) {
      return const SizedBox.shrink();
    }
    final tempMin = detail['temp_min'];
    final tempMax = detail['temp_max'];
    final pop = detail['pop'];
    final humidity = detail['humidity'];
    final uv = detail['uv_index'];
    final windDay = detail['wind_day'];
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.wb_sunny_outlined, size: 18),
                SizedBox(width: 6),
                Text('当天天气', style: TextStyle(fontWeight: FontWeight.w600)),
              ],
            ),
            const SizedBox(height: 8),
            Text(weather ?? '${detail['day'] ?? '-'} / ${detail['night'] ?? '-'}'),
            const SizedBox(height: 6),
            Wrap(
              spacing: 10,
              runSpacing: 6,
              children: [
                if (tempMin != null && tempMax != null) _WeatherPill(icon: Icons.thermostat_outlined, text: '$tempMin-$tempMax℃'),
                if (pop != null) _WeatherPill(icon: Icons.water_drop_outlined, text: '降水 $pop%'),
                if (humidity != null) _WeatherPill(icon: Icons.opacity, text: '湿度 $humidity%'),
                if (uv != null) _WeatherPill(icon: Icons.wb_sunny, text: 'UV $uv'),
                if (windDay != null) _WeatherPill(icon: Icons.air, text: '$windDay'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _WeatherPill extends StatelessWidget {
  const _WeatherPill({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 15),
        const SizedBox(width: 4),
        Text(text, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}

class _AdviceBox extends StatelessWidget {
  const _AdviceBox({required this.advice});

  final List<String> advice;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.secondaryContainer,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.wb_cloudy_outlined, size: 18),
                SizedBox(width: 6),
                Text('天气建议', style: TextStyle(fontWeight: FontWeight.w600)),
              ],
            ),
            const SizedBox(height: 8),
            for (final item in advice) Text('• $item'),
          ],
        ),
      ),
    );
  }
}

class _BudgetBox extends StatelessWidget {
  const _BudgetBox({required this.budget});

  final Map<String, dynamic> budget;

  @override
  Widget build(BuildContext context) {
    final total = budget['total_estimated_cny'];
    return DecoratedBox(
      decoration: BoxDecoration(
        border: Border.all(color: Theme.of(context).colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.account_balance_wallet_outlined, size: 18),
                SizedBox(width: 6),
                Text('预算估算', style: TextStyle(fontWeight: FontWeight.w600)),
              ],
            ),
            const SizedBox(height: 8),
            if (total != null) Text('预计游玩花费：¥$total'),
            Text('餐饮 ¥${budget['food_cny'] ?? '-'} · 交通 ¥${budget['transport_cny'] ?? '-'} · 门票 ¥${budget['tickets_cny'] ?? '-'}'),
            if (budget['notes'] != null) Text('${budget['notes']}', style: Theme.of(context).textTheme.bodySmall),
          ],
        ),
      ),
    );
  }
}

class _DaySummaryCard extends StatelessWidget {
  const _DaySummaryCard({required this.day});

  final Map<String, dynamic> day;

  @override
  Widget build(BuildContext context) {
    final items = _asMapList(day['items']);
    final dayNumber = day['day'] ?? '-';
    final date = day['date'] ?? '';
    final firstItem = items.isEmpty ? null : items.first;
    final firstPlaceValue = firstItem == null ? null : firstItem['place'] ?? firstItem['title'];
    final firstPlace = firstPlaceValue == null ? '暂无安排' : '$firstPlaceValue';
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => DayPlanScreen(day: day)),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              CircleAvatar(child: Text('$dayNumber')),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Day $dayNumber · $date', style: Theme.of(context).textTheme.titleSmall),
                    if (day['theme'] != null) Text('${day['theme']}'),
                    const SizedBox(height: 4),
                    Text(
                      '$firstPlace · 共 ${items.length} 项安排',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    if (day['weather'] != null)
                      Text('${day['weather']}', style: Theme.of(context).textTheme.bodySmall),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    );
  }
}

class _DaySection extends StatelessWidget {
  const _DaySection({required this.day});

  final Map<String, dynamic> day;

  @override
  Widget build(BuildContext context) {
    final items = _asMapList(day['items']);
    return Padding(
      padding: const EdgeInsets.only(bottom: 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Day ${day['day']} · ${day['date']}', style: Theme.of(context).textTheme.titleMedium),
          if (day['theme'] != null) Text('${day['theme']}', style: Theme.of(context).textTheme.bodyMedium),
          if (day['weather'] != null) ...[
            const SizedBox(height: 4),
            Row(
              children: [
                const Icon(Icons.thermostat_outlined, size: 16),
                const SizedBox(width: 4),
                Expanded(child: Text('${day['weather']}', style: Theme.of(context).textTheme.bodySmall)),
              ],
            ),
          ],
          const SizedBox(height: 8),
          for (final item in items) _ItineraryCard(item: item),
        ],
      ),
    );
  }
}

class _ItineraryCard extends StatelessWidget {
  const _ItineraryCard({required this.item});

  final Map<String, dynamic> item;

  @override
  Widget build(BuildContext context) {
    final time = item['time']?.toString() ?? '--:--';
    final timeRange = item['time_range']?.toString() ?? time;
    final photoUrl = item['photo_url']?.toString();
    final amapUrl = item['amap_url']?.toString();
    final timeBlocks = _asStringList(item['time_blocks']);
    final details = _asStringList(item['details']);
    final tips = _asStringList(item['tips']);
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (photoUrl != null && photoUrl.isNotEmpty) ...[
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.network(
                  photoUrl,
                  height: 120,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => const SizedBox.shrink(),
                ),
              ),
              const SizedBox(height: 12),
            ],
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                CircleAvatar(
                  radius: 22,
                  child: Text(time.length >= 2 ? time.substring(0, 2) : '--'),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('${item['title'] ?? item['place'] ?? '安排'}', style: Theme.of(context).textTheme.titleSmall),
                      const SizedBox(height: 4),
                      Text('${item['place'] ?? ''}'),
                      _MetaLine(icon: Icons.schedule, text: timeRange),
                      if (item['schedule_note'] != null) _MetaLine(icon: Icons.timer_outlined, text: '${item['schedule_note']}'),
                      if (item['address'] != null) _MetaLine(icon: Icons.place_outlined, text: '${item['address']}'),
                      if (item['rating'] != null) _MetaLine(icon: Icons.star_border, text: '高德评分 ${item['rating']}'),
                      if (item['restaurant_cost_cny'] != null)
                        _MetaLine(icon: Icons.restaurant_menu, text: '高德人均 ¥${item['restaurant_cost_cny']}'),
                      if (item['route_info'] != null)
                        _MetaLine(icon: Icons.directions_outlined, text: '${item['route_info']}'),
                      if (item['transport'] != null) _MetaLine(icon: Icons.route_outlined, text: '${item['transport']}'),
                      if (item['estimated_cost_cny'] != null) _MetaLine(icon: Icons.payments_outlined, text: '预计 ¥${item['estimated_cost_cny']}'),
                      if (amapUrl != null && amapUrl.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        Align(
                          alignment: Alignment.centerLeft,
                          child: OutlinedButton.icon(
                            onPressed: () => _openAmap(amapUrl),
                            icon: const Icon(Icons.map_outlined),
                            label: const Text('打开高德地图'),
                          ),
                        ),
                      ],
                      if (item['reason'] != null) Padding(
                        padding: const EdgeInsets.only(top: 6),
                        child: Text('${item['reason']}', style: Theme.of(context).textTheme.bodySmall),
                      ),
                      if (timeBlocks.isNotEmpty)
                        _InfoList(title: '时间分配', items: timeBlocks, icon: Icons.view_timeline_outlined),
                      if (details.isNotEmpty)
                        _InfoList(title: '怎么玩', items: details, icon: Icons.tour_outlined),
                      if (tips.isNotEmpty)
                        _InfoList(title: '注意事项', items: tips, icon: Icons.info_outline),
                      if (item['backup'] != null) Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Text('备选：${item['backup']}', style: Theme.of(context).textTheme.bodySmall),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _openAmap(String url) async {
    final uri = Uri.parse(url);
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      await launchUrl(uri, mode: LaunchMode.platformDefault);
    }
  }
}

class _InfoList extends StatelessWidget {
  const _InfoList({required this.title, required this.items, required this.icon});

  final String title;
  final List<String> items;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Padding(
          padding: const EdgeInsets.all(10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(icon, size: 16),
                  const SizedBox(width: 6),
                  Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
                ],
              ),
              const SizedBox(height: 6),
              for (final item in items) Text('• $item', style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        ),
      ),
    );
  }
}

class _MetaLine extends StatelessWidget {
  const _MetaLine({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 4),
      child: Row(
        children: [
          Icon(icon, size: 15),
          const SizedBox(width: 4),
          Expanded(child: Text(text, style: Theme.of(context).textTheme.bodySmall)),
        ],
      ),
    );
  }
}

List<Map<String, dynamic>> _asMapList(dynamic value) {
  if (value is! List) return [];
  return value.whereType<Map>().map((item) => Map<String, dynamic>.from(item)).toList();
}

List<String> _asStringList(dynamic value) {
  if (value is! List) return [];
  return value.map((item) => '$item').toList();
}

Map<String, dynamic> _asMap(dynamic value) {
  if (value is! Map) return {};
  return Map<String, dynamic>.from(value);
}
