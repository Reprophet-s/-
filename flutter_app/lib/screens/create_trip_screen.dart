import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../services/api_client.dart';
import 'trip_detail_screen.dart';

class CreateTripScreen extends StatefulWidget {
  const CreateTripScreen({super.key});

  @override
  State<CreateTripScreen> createState() => _CreateTripScreenState();
}

class _CreateTripScreenState extends State<CreateTripScreen> {
  final _formKey = GlobalKey<FormState>();
  final _api = ApiClient();
  final _destinationController = TextEditingController(text: '杭州');
  final _budgetController = TextEditingController(text: '3000');
  final _hotelController = TextEditingController();
  final _avoidController = TextEditingController(text: '过度排队,太赶');
  final _notesController = TextEditingController();
  final Set<String> _interests = {'美食', '自然风光', '历史文化'};
  DateTime _startDate = DateTime.now().add(const Duration(days: 7));
  int _days = 3;
  int _travelers = 2;
  String _pace = 'balanced';
  bool _loading = false;

  static const _destinationOptions = ['北京', '广州', '西双版纳', '上海', '长沙', '武汉', '杭州', '苏州'];
  static const _interestOptions = ['美食', '博物馆', '自然风光', '历史文化', '亲子', '夜景', '购物', '咖啡', '徒步'];

  @override
  void dispose() {
    _destinationController.dispose();
    _budgetController.dispose();
    _hotelController.dispose();
    _avoidController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      final trip = await _api.createTrip({
        'destination': _destinationController.text.trim(),
        'start_date': DateFormat('yyyy-MM-dd').format(_startDate),
        'days': _days,
        'travelers': _travelers,
        'budget_cny': int.tryParse(_budgetController.text.trim()),
        'interests': _interests.toList(),
        'pace': _pace,
        'hotel_address': _emptyToNull(_hotelController.text),
        'avoid': _splitTags(_avoidController.text),
        'notes': _emptyToNull(_notesController.text),
      });
      if (!mounted) return;
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => TripDetailScreen(initialTrip: trip)),
      );
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$error')));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String? _emptyToNull(String value) {
    final trimmed = value.trim();
    return trimmed.isEmpty ? null : trimmed;
  }

  List<String> _splitTags(String value) {
    return value
        .split(RegExp(r'[,，]'))
        .map((item) => item.trim())
        .where((item) => item.isNotEmpty)
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI 旅行计划')),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              TextFormField(
                controller: _destinationController,
                decoration: const InputDecoration(labelText: '目的地', prefixIcon: Icon(Icons.place_outlined)),
                validator: (value) => value == null || value.trim().isEmpty ? '请输入目的地' : null,
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (final destination in _destinationOptions)
                    ActionChip(
                      avatar: const Icon(Icons.location_city_outlined, size: 16),
                      label: Text(destination),
                      onPressed: () => setState(() => _destinationController.text = destination),
                    ),
                ],
              ),
              const SizedBox(height: 12),
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.event_outlined),
                title: const Text('出发日期'),
                subtitle: Text(DateFormat('yyyy-MM-dd').format(_startDate)),
                trailing: const Icon(Icons.chevron_right),
                onTap: _pickDate,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(child: _StepperField(label: '天数', value: _days, min: 1, max: 30, onChanged: (v) => setState(() => _days = v))),
                  const SizedBox(width: 12),
                  Expanded(child: _StepperField(label: '人数', value: _travelers, min: 1, max: 20, onChanged: (v) => setState(() => _travelers = v))),
                ],
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: _pace,
                decoration: const InputDecoration(labelText: '游玩节奏', prefixIcon: Icon(Icons.speed_outlined)),
                items: const [
                  DropdownMenuItem(value: 'relaxed', child: Text('轻松')),
                  DropdownMenuItem(value: 'balanced', child: Text('均衡')),
                  DropdownMenuItem(value: 'packed', child: Text('充实')),
                ],
                onChanged: (value) => setState(() => _pace = value ?? 'balanced'),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _budgetController,
                decoration: const InputDecoration(labelText: '总预算（元，不含酒店/大交通）', prefixIcon: Icon(Icons.payments_outlined)),
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 16),
              Text('兴趣偏好', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (final interest in _interestOptions)
                    FilterChip(
                      label: Text(interest),
                      selected: _interests.contains(interest),
                      onSelected: (selected) {
                        setState(() {
                          if (selected) {
                            _interests.add(interest);
                          } else {
                            _interests.remove(interest);
                          }
                        });
                      },
                    ),
                ],
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _hotelController,
                decoration: const InputDecoration(labelText: '酒店/住宿位置（可选）', prefixIcon: Icon(Icons.hotel_outlined)),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _avoidController,
                decoration: const InputDecoration(labelText: '想避免的情况，用逗号分隔', prefixIcon: Icon(Icons.block_outlined)),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _notesController,
                decoration: const InputDecoration(labelText: '补充需求（可选）', prefixIcon: Icon(Icons.edit_note_outlined)),
                minLines: 2,
                maxLines: 4,
              ),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: _loading ? null : _submit,
                icon: _loading
                    ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Icon(Icons.auto_awesome),
                label: const Text('生成最佳旅行计划'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _startDate,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (picked != null) setState(() => _startDate = picked);
  }
}

class _StepperField extends StatelessWidget {
  const _StepperField({
    required this.label,
    required this.value,
    required this.min,
    required this.max,
    required this.onChanged,
  });

  final String label;
  final int value;
  final int min;
  final int max;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    return InputDecorator(
      decoration: InputDecoration(labelText: label),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            tooltip: '减少',
            onPressed: value <= min ? null : () => onChanged(value - 1),
            icon: const Icon(Icons.remove),
          ),
          Text('$value', style: Theme.of(context).textTheme.titleMedium),
          IconButton(
            tooltip: '增加',
            onPressed: value >= max ? null : () => onChanged(value + 1),
            icon: const Icon(Icons.add),
          ),
        ],
      ),
    );
  }
}
