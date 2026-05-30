import 'dart:convert';

import 'package:http/http.dart' as http;

import '../app_config.dart';
import '../models/trip.dart';

class ApiClient {
  ApiClient({this.baseUrl = AppConfig.apiBaseUrl});

  final String baseUrl;

  Future<Trip> createTrip(Map<String, dynamic> payload) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/trips'),
      headers: {'content-type': 'application/json'},
      body: jsonEncode(payload),
    );
    _ensureSuccess(response);
    return Trip.fromJson(jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
  }

  Future<Trip> getTrip(String id) async {
    final response = await http.get(Uri.parse('$baseUrl/api/trips/$id'));
    _ensureSuccess(response);
    return Trip.fromJson(jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
  }

  Future<Trip> regenerateTrip(String id) async {
    final response = await http.post(Uri.parse('$baseUrl/api/trips/$id/generate'));
    _ensureSuccess(response);
    return Trip.fromJson(jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
  }

  void _ensureSuccess(http.Response response) {
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('API ${response.statusCode}: ${response.body}');
    }
  }
}
