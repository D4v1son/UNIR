for i=1, 10 do
    redis.call('set', 'key_' .. i, i)
end