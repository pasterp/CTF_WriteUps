require "socket"
require "openssl"
require "base64"

host = "challenge.404ctf.fr"
port = 32128

s = TCPSocket.new host, port

puts s.gets
c = s.gets.to_i.to_bn
puts s.gets
n = s.gets.split(" ")[2].to_i.to_bn
puts "[i] n=#{n}"
e = s.gets.split(" ")[2].to_i.to_bn
puts "[i] e=#{e}"
puts s.gets
puts s.gets
puts s.gets

v = (rand(64)).to_bn
ca = v.mod_exp(e, n)

cb = ca * c
puts "[>] Sending (#{v}) cb"
s.puts cb
puts s.gets
cbd = s.gets.to_i
puts "[<] Received cb^d = #{cbd}"

hex = t.to_s(16)
puts "#{hex}"
puts "#{[hex].pack("H*")}"

# 404CTF{L3s_0r4cl3s_RSA_s0n7_si_fr4g1l35}
