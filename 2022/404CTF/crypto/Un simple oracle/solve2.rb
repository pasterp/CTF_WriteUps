require "socket"
require "openssl"
require "base64"
require "prime"

host = "challenge.404ctf.fr"
port = 30594

s = TCPSocket.new host, port

puts s.gets
puts s.gets
c = s.gets.split(" ").last.to_i.to_bn
puts "[*] c = #{c}"
puts s.gets
e = s.gets.split(" ")[2].to_i.to_bn
puts "[i] e=#{e}"
puts s.gets
puts s.gets
puts s.gets

# En utilisant -1 il est simple de retrouver N
s.puts -1
puts s.gets
n = s.gets.to_i - (-1).pow(e)
s.gets
puts "[*] n= #{n}"

v = (rand(64)).to_bn
ca = v.mod_exp(e, n)

cb = ca * c
puts "[>] Sending (#{v}) cb=#{cb}"
s.puts cb
puts s.gets
cbd = s.gets.to_i
puts "[<] Received cb^d = #{cbd}"

t = cbd / v
hex = t.to_s(16)
puts "#{hex}"
puts "#{[hex].pack("H*")}"

# 404CTF{L3_m0dul3_357_t0uj0ur5_7r0uv4bl3}
