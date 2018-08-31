import sys
import spotipy
import spotipy.util as util
from collections import Counter
from math import sqrt
from Tkinter import *

scope = 'user-library-read'
username = '*************'

class Application(Frame):
    def say_hi(self):
        print "hi there, everyone!"

    def createWidgets(self):
        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})

        self.hi_there = Button(self)
        self.hi_there["text"] = "Hello",
        self.hi_there["command"] = self.say_hi

        self.hi_there.pack({"side": "left"})
        filemenu = Menu(menubar, tearoff=0)


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()



class suitability():
    
    def __init__(self, bpm, dance, energy, loud, speech, acoustic, instrumental, live, positive, date, label_frequency, artist_frequency, related_artists, genres):
        self.bpm = bpm
        self.dance = dance
        self.energy = energy
        self.loud = loud
        self.speech = speech
        self.acoustic = acoustic
        self.instrumental = instrumental
        self.live = live
        self.positive = positive
        self.date = date
        self.labels = label_frequency
        self.artists = artist_frequency
        self.related_artists = related_artists
        self.genres = genres

class track():

    def __init__(self,artist_name, artist_id,track_name, track_id, album_id):
        self.artist_name = artist_name
        self.artist_id = artist_id
        self.track_name = track_name
        self.track_id = track_id
        self.album_id = album_id
        self.genres = []
        self.label = ''
        
class playlist():  
    def __init__(self,playlist_name, playlist_id, playlist_total, playlist_tracks):
        self.playlist_name = playlist_name
        self.playlist_id = playlist_id
        self.playlist_total = playlist_total
        self.playlist_tracks  = playlist_tracks
        self.tags = suitability(None, None, None, None, None, None, None, None, None, None, [], [], [], [])
        

    def analyse(self):
        self.genre_count = Counter()
        self.label_count = Counter()
        self.artist_frequency = []
        self.pl_date = [[],()]
        self.pl_bpm = [[],()]
        self.pl_dance = [[],()]
        self.pl_energy = [[],()]
        self.pl_loud = [[],()]
        self.pl_speech = [[],()]
        self.pl_acoustic = [[],()]
        self.pl_instrumental = [[],()]
        self.pl_live = [[],()]
        self.pl_positive = [[],()]
        track_ids = []
        artist_ids = []
        album_ids = []
        for playlist_track in self.playlist_tracks:
            track_ids.append(playlist_track.track_id)
            artist_ids.append(playlist_track.artist_id)
            album_ids.append(playlist_track.album_id)
            self.artist_frequency.append(playlist_track.artist_name)        
        self.artist_frequency = Counter(self.artist_frequency)
        x = 0
        for i in xrange(0, len(artist_ids), 50):
            for item in sp.artists(artist_ids[((i/50)*50):((i/50)*50)+50])['artists']:
                self.playlist_tracks[x].genres = item['genres']
                self.genre_count.update(item['genres'])
                x += 1
        x = 0
        for i in xrange(0, len(album_ids), 20):
            for item in sp.albums(album_ids[((i/20)*20):((i/20)*20)+20])['albums']:
                self.pl_date[0].append(int(item['release_date'][0:4]))
                self.playlist_tracks[x].label = item['label']
                self.label_count.update([item['label']])
                x += 1
        self.pl_date[1] = stddev(self.pl_date[0])
        for item in sp.audio_features(track_ids):
            self.pl_bpm[0].append(item['tempo'])
            self.pl_dance[0].append(item['danceability'])
            self.pl_energy[0].append(item['energy'])
            self.pl_loud[0].append(item['loudness'])
            self.pl_speech[0].append(item['speechiness'])
            self.pl_acoustic[0].append(item['acousticness'])
            self.pl_instrumental[0].append(item['instrumentalness'])
            self.pl_live[0].append(item['liveness'])
            self.pl_positive[0].append(item['valence'])
        self.pl_bpm[1] = stddev(self.pl_bpm[0])
        self.pl_dance[1] = stddev(self.pl_dance[0])
        self.pl_energy[1] = stddev(self.pl_energy[0])
        self.pl_loud[1] = stddev(self.pl_loud[0])
        self.pl_speech[1] = stddev(self.pl_speech[0])
        self.pl_acoustic[1] = stddev(self.pl_acoustic[0])
        self.pl_instrumental[1] = stddev(self.pl_instrumental[0])
        self.pl_live[1] = stddev(self.pl_live[0])
        self.pl_positive[1] = stddev(self.pl_positive[0])


def get_user_playlists():
    playlists = sp.user_playlists(username)
    user_playlists =[]
    for user_playlist in playlists['items']:
        user_playlists.append(playlist(user_playlist['name'],user_playlist['id'],user_playlist['tracks']['total'],get_tracks(user_playlist['id'])))
    return user_playlists

        
def get_tracks(id):
    results = sp.user_playlist(username, id, fields="tracks,next")
    tracks = results['tracks']
    playlist_tracks = []
    for i, item in enumerate(tracks['items']):
        playlist_track = item['track']
        playlist_tracks.append(track(playlist_track['artists'][0]['name'],playlist_track['artists'][0]['id'],playlist_track['name'],playlist_track['id'],item['track']['album']['id']))
    return playlist_tracks


def related_artists(artist_id, form):
    related = []
    for artists in sp.artist_related_artists(artist_id)['artists']:
        related.append(artists[form])
    return related


def year_and_label(song_id):
    return (sp.album(sp.track(song_id)['album']['id'])['release_date'][:4]
            ,sp.album(sp.track(song_id)['album']['id'])['label'])

def stddev(list):
    mean = float(sum(list)) / len(list)
    return (sqrt(float(reduce(lambda x, y: x + y, map(lambda x: (x - mean) ** 2, list))) / len(list)), mean)
    


def similarity_check(track_number, playlist_to_sort, user_playlists):
    suitabilities = []
    tags = []
    print "{} : {}".format(playlist_to_sort.playlist_tracks[track_number].artist_name,playlist_to_sort.playlist_tracks[track_number].track_name)
    for user_playlist in user_playlists:
        related_tag = []
        genre_tag = []
        artist_tag = []
        label_tag = []
        genre_in_common = {}
        for genre in playlist_to_sort.playlist_tracks[track_number].genres:
            genre_in_common[genre] = (user_playlist.genre_count[genre]/float(len(user_playlist.playlist_tracks)))*100
            if user_playlist.tags.genres != None:
                if genre in user_playlist.tags.genres:
                    genre_tag.append(genre) 
            else:
                genre_tag = None
        related_in_playlist = 0
        for related_artist in related_artists(playlist_to_sort.playlist_tracks[track_number].artist_id,'name'):
            related_in_playlist += user_playlist.artist_frequency[related_artist]
            if user_playlist.tags.related_artists != None:
                if related_artist in user_playlist.tags.related_artists:
                    related_tag.append(related_artist)
            else:
                related_tag = None
               
        suitabilities.append(suitability((user_playlist.pl_bpm[1][1]-user_playlist.pl_bpm[1][0]) <= playlist_to_sort.pl_bpm[0][track_number] <= (user_playlist.pl_bpm[1][1]+user_playlist.pl_bpm[1][0]),
                               (user_playlist.pl_dance[1][1]-user_playlist.pl_dance[1][0]) <= playlist_to_sort.pl_dance[0][track_number] <= (user_playlist.pl_dance[1][1]+user_playlist.pl_dance[1][0]),
                               (user_playlist.pl_energy[1][1]-user_playlist.pl_energy[1][0]) <= playlist_to_sort.pl_energy[0][track_number] <= (user_playlist.pl_energy[1][1]+user_playlist.pl_energy[1][0]),
                               (user_playlist.pl_loud[1][1]-user_playlist.pl_loud[1][0]) <= playlist_to_sort.pl_loud[0][track_number] <= (user_playlist.pl_loud[1][1]+user_playlist.pl_loud[1][0]),
                               (user_playlist.pl_speech[1][1]-user_playlist.pl_speech[1][0]) <= playlist_to_sort.pl_speech[0][track_number] <= (user_playlist.pl_speech[1][1]+user_playlist.pl_speech[1][0]),
                               (user_playlist.pl_acoustic[1][1]-user_playlist.pl_acoustic[1][0]) <= playlist_to_sort.pl_acoustic[0][track_number] <= (user_playlist.pl_acoustic[1][1]+user_playlist.pl_acoustic[1][0]),
                               (user_playlist.pl_instrumental[1][1]-user_playlist.pl_instrumental[1][0]) <= playlist_to_sort.pl_instrumental[0][track_number] <= (user_playlist.pl_instrumental[1][1]+user_playlist.pl_instrumental[1][0]),
                               (user_playlist.pl_live[1][1]-user_playlist.pl_live[1][0]) <= playlist_to_sort.pl_live[0][track_number] <= (user_playlist.pl_live[1][1]+user_playlist.pl_live[1][0]),
                               (user_playlist.pl_positive[1][1]-user_playlist.pl_positive[1][0]) <= playlist_to_sort.pl_positive[0][track_number] <= (user_playlist.pl_positive[1][1]+user_playlist.pl_positive[1][0]),
                               (user_playlist.pl_date[1][1]-user_playlist.pl_date[1][0]) <= playlist_to_sort.pl_date[0][track_number] <= (user_playlist.pl_date[1][1]+user_playlist.pl_date[1][0]),
                               (float(user_playlist.label_count[playlist_to_sort.playlist_tracks[track_number].label])/ float(sum(user_playlist.label_count.values())))*100,
                               (float(user_playlist.artist_frequency[playlist_to_sort.playlist_tracks[track_number].artist_name])/float(sum(user_playlist.artist_frequency.values())))*100,
                               (float(related_in_playlist)/float(sum(user_playlist.artist_frequency.values())))*100,
                               genre_in_common
                              ))

        if user_playlist.tags.labels != None:
            print playlist_to_sort.playlist_tracks[track_number].label
            if playlist_to_sort.playlist_tracks[track_number].label in user_playlist.tags.labels:
                label_tag.append(playlist_to_sort.playlist_tracks[track_number].label)
        else:
            label_tag = None          
        if user_playlist.tags.artists != None:
            if playlist_to_sort.playlist_tracks[track_number].artist_name in user_playlist.tags.artists:
                artist_tag.append(playlist_to_sort.playlist_tracks[track_number].artist_name)
        else:
            artist_tag = None
        
        tags.append(suitability(bound_test(user_playlist.tags.bpm, playlist_to_sort.pl_bpm[0][track_number]),
                                bound_test(user_playlist.tags.dance, playlist_to_sort.pl_dance[0][track_number]),
                                bound_test(user_playlist.tags.energy, playlist_to_sort.pl_energy[0][track_number]),
                                bound_test(user_playlist.tags.loud, playlist_to_sort.pl_loud[0][track_number]),
                                bound_test(user_playlist.tags.speech, playlist_to_sort.pl_speech[0][track_number]),
                                bound_test(user_playlist.tags.acoustic, playlist_to_sort.pl_acoustic[0][track_number]),
                                bound_test(user_playlist.tags.instrumental, playlist_to_sort.pl_instrumental[0][track_number]),
                                bound_test(user_playlist.tags.live, playlist_to_sort.pl_live[0][track_number]),
                                bound_test(user_playlist.tags.positive, playlist_to_sort.pl_positive[0][track_number]),
                                bound_test(user_playlist.tags.date, playlist_to_sort.pl_date[0][track_number]),
                                label_tag,
                                artist_tag,
                                related_tag,
                                genre_tag
                                ))

        
    return (suitabilities, tags)


def bound_test(upper_lower, value):
    if upper_lower != None:
        print value
        print upper_lower
        print upper_lower[0] <= value <= upper_lower[1]
        return upper_lower[0] <= value <= upper_lower[1]
    else:
        return None
        
def add_tag(playlist, tag_type):
    if tag_type == 1:
        genre_file = open('genres.txt','r')
        all_genres = genre_file.read()
        print all_genres
        genre_file = open('genres.txt','r')
        all_genres = genre_file.readlines()
        chosen_genre = input('Choose a genre to tag')
        playlist.tags.genres.append(all_genres[chosen_genre].encode('utf-8').strip('\n'))
        print all_genres[chosen_genre]
    elif tag_type == 2:
        artist_name = raw_input("artist name")
        playlist.tags.artists.append(artist_name)
        if raw_input("Related aswell? Y/N") == 'Y':
            playlist.tags.related_artists.append(artist_name)
    elif tag_type == 3:
        label_name = raw_input("label name")
        playlist.tags.labels.append(label_name)
    else:
        lower = input("lower")
        upper = input("upper")
        if tag_type == 4:
            playlist.tags.bpm = (lower, upper)
        if tag_type == 5:
            playlist.tags.date = (lower, upper)
        if tag_type == 6:
            playlist.tags.dance = (lower, upper)
        if tag_type == 7:
            playlist.tags.energy = (lower, upper)
        if tag_type == 8:
            playlist.tags.speech = (lower, upper)
        if tag_type == 9:
            playlist.tags.acoustic = (lower, upper)
        if tag_type == 10:
            playlist.tags.live = (lower, upper)
        if tag_type == 11:
            playlist.tags.positive = (lower, upper)
        

def suggest_playlists(similarity, playlists):
    for i, similarity_check in enumerate(similarity[1]):
        print playlists[i].playlist_name
        print 'genre match :                    {}'.format(similarity_check.genres)
        print 'artist match :                   {}'.format(similarity_check.artists)
        print 'related artist match :           {}'.format(similarity_check.related_artists)
        print 'label similarity match :         {}'.format(similarity_check.labels)
        print 'bpm match {} :                   {}'.format(none_check(playlists[i].tags.bpm),similarity_check.bpm)
        print 'release match {} :               {}'.format(none_check(playlists[i].tags.date),similarity_check.date)
        print 'dance match {} :                 {}'.format(none_check(playlists[i].tags.dance),similarity_check.dance)
        print 'energy match {} :                {}'.format(none_check(playlists[i].tags.energy),similarity_check.energy)
        print 'speech match {} :                {}'.format(none_check(playlists[i].tags.speech),similarity_check.speech)
        print 'acoustic match {} :              {}'.format(none_check(playlists[i].tags.acoustic),similarity_check.acoustic)
        print 'live match {} :                  {}'.format(none_check(playlists[i].tags.live),similarity_check.live)
        print 'positive match {} :              {}'.format(none_check(playlists[i].tags.positive),similarity_check.positive)
        print ' '
def none_check(tag):
    if tag != None:
        return '{} - {}'.format(tag[0],tag[1])
    else:
        return ' '

def donothing():
   filewin = Toplevel(root)
   button = Button(filewin, text="Do nothing button")
   button.pack()
   
if __name__ == "__main__":
    token = util.prompt_for_user_token(username,scope,client_id='**************',client_secret='************',redirect_uri='http://example.com/callback/')

'''    
 
    if token:
        sp = spotipy.Spotify(auth=token)
        user_playlists = get_user_playlists()
        while True:
            print '1.Sort a playlist'
            print '2.Add a tag'
            function = input('Choose a function')
            for i, user_playlist in enumerate(user_playlists):
                print("{} : {}".format(i, user_playlist.playlist_name))
            chosen_playlist = input('Choose a playlist: ') 
            if function == 1:
                for i, user_playlist in enumerate(user_playlists):
                    if(i != chosen_playlist):
                        print ('analysing {}...'.format(i))
                        user_playlist.analyse()
                    else:
                        print ('analysing {}...'.format(i))
                        user_playlist.analyse()
                playlist_to_sort = user_playlists[chosen_playlist]
                del user_playlists[chosen_playlist]
                for i in xrange(len(playlist_to_sort.playlist_tracks)):
                    suggest_playlists(similarity_check(i, playlist_to_sort, user_playlists), user_playlists)
                    playlist = input("which playlist/ 12 to go back")
                    if playlist == 12:
                        break
            if function == 2:
                while True:
                    print '1.Genre'
                    print '2.Artists'
                    print '3.Label'
                    print '4.Bpm'
                    print '5.release'
                    print '6.Dance'
                    print '7.Energy'
                    print '8.Speech'
                    print '9.Acousticness'
                    print '10.Live'
                    print '11.Positive'
                    print '12 to go back'
                    function = input('Choose a function')
                    if function == 12:
                        break
                    add_tag(user_playlists[chosen_playlist], function)

                    

    else:
        print ("Can't get token for", username)
'''
