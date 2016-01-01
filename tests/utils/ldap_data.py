class LDAPTestDirectory(object):


    top = ('o=test', {'o': 'test'})
    example = ('ou=example,o=test', {'ou': 'example'})
    admin = ('cn=admin,ou=example,o=test',
             {
                 'cn': 'admin',
                 'userPassword': ['ldaptest']
             })
    alice = ('uid=alice,ou=example,o=test',
             {
                 'cn': 'Alice Waters',
                 'uid': 'alice',
                 'mail': 'alice@example.com',
                 'userPassword': ['alicepw'],
                 'sambaNTPassword': ['bobpw']
             })
    bob = ('uid=bob,ou=example,o=test',
           {
               'cn': 'Bob Vila',
               'uid': 'bob',
               'mail': 'bob@example.com',
               'userPassword': ['bobpw'],
               'sambaNTPassword': ['bobpw'],
               'sshPublicKey': [
                   'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCZeHe71ej4gNwhwFrLMn7OY5UNMpCGII9pNJZ+gtHjBZ5cT8mzwSDqbOG3/yeQyhfZdZUjJuD8fFdYsKvPSMUgUahjxCp50BbT2sxRwE+9ij5QukZAJCG2ggM9TcEx9sFWMk1IDT72u0AOjKeYcImfAm/4Z0PcH6ozlUjyfJspb7LG5fxxkuxVdOQ6ZWWHxA7Ckf4JzxCVxmbVDl2BAC98t/MIWwcUGg3fv2UTKwhU7cWflVjxkVEtG2OYImI1jQfYs/sSD2BcmagXwZxBzPHLuu/zSLh/OzJYcf9RKR4t2AgQqpx5g9A0SVw1R/we4Cpm7MmGaNjxif0pBS/BWTxJ bob@example.test',
                   'ssh-dss AAAAB3NzaC1kc3MAAACBAKDBr7RQkFHQd95FGW3dMV7Rxc/IW2m2iDhVg1fDrHPfeQdV2IezMNgp7JWq4e94STSuyxUdr3gngXVamxeMUnnigIY92NjU4g971IPF2ttuHBQpaMs7rcnZZJl73X9xJZ2yHtwR+x/ey9QmeKwVis7GY5VECG2w+j7WP6HV4HZNAAAAFQDgvtc4zanxvJdc5pFgFudzE37jLQAAAIEAkY+b69evVzvjbzc8z+RjHeeFD2wvITXMCNmqYue2i1DSDHyyuX8MhU0QxlV2q9XtgEQ+PJPqIkGo+9PDFBXok/a/FXlHV0rJCuO/CnSOmiCadcrdlKEIPY/QyPxNwbbARHBfXpfWWQvsTqhbWAx+/+A2ITWqxGgdfcudj92m8P4AAACADvigz/c7xx8wqmAddLEDc3ODnfjOE6KVxBsr0eckr34ccpHGXtCDZkQLlBFbXvHet+kMzGj/udm/XqJi5o638PnD2MoVEJMiylDpvw0idEuJcfAMHvK92IC/hmXk3OQRFnHtpGohCL31MBfoVrXYM3IiM/SCFYHq5CEjRsETlqE= bob@example.test'
                   ]
           })
    baduser = ('uid=baduser,ou=example,o=test',
               {
                   'cn': 'baduser',
                   'userPassword': ['baduserpw'],
                   'sshPublicKey': [
                       'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCZeHe71ej4gNwhwFrLMn7OY5UNMpCGII9pNJZ+gtHjBZ5cT8mzwSDqbOG3/yeQyhfZdZUjJuD8fFdYsKvPSMUgUahjxCp50BbT2sxRwE+9ij5QukZAJCG2ggM9TcEx9sFWMk1IDT72u0AOjKeYcImfAm/4Z0PcH6ozlUjyfJspb7LG5fxxkuxVdOQ6ZWWHxA7Ckf4JzxCVxmbVDl2BAC98t/MIWwcUGg3',
                       'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCZeHe71ej4gNwhwFrLMn7OY5UNMpCGII9pNJZ+gtHjBZ5cT8mzwSDqbOG3/yeQyj5QukZAJCG2ggM9TcEx9sFWMk1IDT72u0AOjKeYcImfAm/4Z0PcH6ozlUjyfJspb7LG5fxxkuxVdOQ6ZWWHxA7Ckf4JzxCVxmbVDl2BAC98t/ badkey@example.test'
                   ]
               })

    directory = dict([top, example, admin, alice, bob, baduser])
