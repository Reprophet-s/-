class Trip {
  Trip({
    required this.id,
    required this.status,
    required this.destination,
    this.plan,
    this.error,
  });

  final String id;
  final String status;
  final String destination;
  final Map<String, dynamic>? plan;
  final String? error;

  factory Trip.fromJson(Map<String, dynamic> json) {
    final request = json['request'] as Map<String, dynamic>;
    return Trip(
      id: json['id'] as String,
      status: json['status'] as String,
      destination: request['destination'] as String,
      plan: json['plan'] == null ? null : Map<String, dynamic>.from(json['plan'] as Map),
      error: json['error'] as String?,
    );
  }
}
